import os
import io
from PIL import Image
import bcrypt
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import time
import numpy as np
import cv2
from utils.classifier import classify_image

load_dotenv()

# Obtendo os valores das variáveis de ambiente
host = os.getenv('DB_HOST', 'localhost')
port = os.getenv('DB_PORT', 5432)
database = os.getenv('DB_DATABASE', 'LeisHticIA_gold')
user = os.getenv('DB_USER', 'postgres')
password = os.environ.get("PG_PASSWORD")

# Configurando a conexão com o banco de dados usando SQLAlchemy
DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"


@st.cache_resource
def get_engine():
    """
    Retorna o engine do SQLAlchemy para conexão com o banco de dados.
    """
    return create_engine(DATABASE_URL)


# Inicializando o SessionMaker
engine = get_engine()
Session = sessionmaker(bind=engine)


# Página de login/cadastro do médico
def medico_login():
    st.title("Login do Médico")
    username = st.text_input("Nome")
    password = st.text_input("Senha", type="password")
    login_button = st.button("Entrar")
    register_button = st.button("Cadastrar-se")

    if login_button:
        session = Session()
        try:
            query = text("SELECT * FROM MEDICO WHERE NOME = :username")
            result = session.execute(
                query, {"username": username}).mappings().fetchone()

            if result and bcrypt.checkpw(password.encode('utf-8'), bytes(result["senha"])):
                st.success("Login realizado com sucesso!")
                st.session_state["medico_logged_in"] = True
                st.session_state["medico_user"] = result
            else:
                st.error("Usuário ou senha inválidos!")
        except Exception as e:
            st.error(f"Erro ao conectar ao banco: {e}")
        finally:
            session.close()

    if register_button:
        st.session_state["show_register"] = True
        st.rerun()


# Página de cadastro do medico
def medico_register():
    st.title("Cadastro do Médico")
    nome = st.text_input("Nome")
    senha = st.text_input("Senha", type="password")
    hospital = st.text_input("Hospital")
    submit = st.button("Cadastrar")

    if submit:
        if not nome or not hospital or not senha:
            st.error("Por favor, preencha todos os campos.")
            return
        hashed_password = bcrypt.hashpw(
            senha.encode('utf-8'), bcrypt.gensalt(12))
        session = Session()
        try:
            query = text("""
                INSERT INTO MEDICO (NOME, SENHA, HOSPITAL)
                VALUES (:nome, :senha, :hospital)
            """)
            session.execute(query, {
                "nome": nome,
                "senha": hashed_password,
                "hospital": hospital
            })
            session.commit()
            st.success("Cadastro realizado com sucesso!")
            time.sleep(2)
            st.session_state["show_register"] = False
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao inserir dados: {e}")
            session.rollback()
        finally:
            session.close()


def medico_area():
    if "medico_logged_in" not in st.session_state or not st.session_state["medico_logged_in"]:
        if "show_register" in st.session_state and st.session_state["show_register"]:
            medico_register()
        else:
            medico_login()
    else:
        st.success(f"Bem-vindo, Dr(a). {st.session_state['medico_user']['nome']}!")
        st.write("Agora você pode melhorar a qualidade de vida dos pacientes!")

        # Inicializa estados no session_state
        if "image" not in st.session_state:
            st.session_state["image"] = None
        if "resultado" not in st.session_state:
            st.session_state["resultado"] = None
        if "camera_open" not in st.session_state:
            st.session_state["camera_open"] = False

        # Botão para abrir/fechar câmera
        if st.button("📷 Abrir/Fechar Câmera"):
            st.session_state["camera_open"] = not st.session_state["camera_open"]
            st.rerun()

        # Exibir câmera se estiver aberta
        if st.session_state["camera_open"]:
            captured_image = st.camera_input("Tire uma foto!")
            if captured_image:
                try:
                    file_bytes = np.asarray(bytearray(captured_image.read()), dtype=np.uint8)
                    st.session_state["image"] = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                    resultado = classify_image(st.session_state["image"])
                    st.session_state["resultado"] = resultado
                except Exception as e:
                    st.error(f"Erro ao processar a imagem: {e}")

        # Mostrar imagem capturada
        if st.session_state["image"] is not None:
            st.image(st.session_state["image"], channels="BGR", width=300)

        # Botão para limpar
        if st.button("❌ Limpar"):
            st.session_state["image"] = None
            st.session_state["resultado"] = None
            st.rerun()

        # Entrada e busca de informações do paciente
        paciente_name = st.text_input("Nome do Paciente")
        if st.button("🔍 Informações do Paciente"):
            session = Session()
            try:
                query = text('''SELECT  NOME, DATA_DE_NASCIMENTO, ENDERECO, CEP, TELEFONE,
                                TEMPO_COM_A_LESAO, HISTORICO_DIABETES, HISTORICO_CANCER,
                                ANTI_INFLAMATORIO_SEM_EFEITO, IMAGEM_LESAO
                                FROM PACIENTE
                                WHERE NOME = :nome''')
                result = session.execute(query, {"nome": paciente_name}).mappings().fetchone()
                if result:
                    dados_paciente = {key: value for key, value in result.items() if key != "imagem_lesao"}
                    st.table([dados_paciente])
                    imagem_lesao_bytes = result["imagem_lesao"]
                    imagem_lesao = Image.open(io.BytesIO(imagem_lesao_bytes))
                    st.image(imagem_lesao, caption="Imagem da Lesão registrada em nosso sistema", use_container_width=True)
                    file_bytes = np.asarray(bytearray(imagem_lesao_bytes), dtype=np.uint8)
                    st.session_state["image"] = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                    classificacao = classify_image(st.session_state["image"])
                    st.session_state["resultado"] = classificacao
                else:
                    st.warning("Paciente não encontrado.")
            except Exception as e:
                st.error(f"Erro ao obter dados do paciente: {e}")
            finally:
                session.close()
