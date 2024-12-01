import os
import time
import bcrypt
import streamlit as st
from dotenv import load_dotenv
import cv2
import numpy as np
from utils.classifier import classify_image
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

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


# Página de login para o paciente
def patient_login():
    st.subheader("Login do Paciente")
    username = st.text_input("Nome de Usuário")
    password = st.text_input("Senha", type="password")
    login_button = st.button("Entrar")
    register_button = st.button("Cadastrar-se")

    if login_button:
        session = Session()
        try:
            query = text("SELECT * FROM PACIENTE WHERE NOME = :username")
            result = session.execute(
                query, {"username": username}).mappings().fetchone()

            # Converte a senha armazenada para bytes, se necessário
            stored_password = result["senha"]
            stored_password = bytes(stored_password)

            if result and bcrypt.checkpw(password.encode('utf-8'), stored_password):
                st.success("Login realizado com sucesso!")
                st.session_state["logged_in"] = True
                st.session_state["user"] = result

            else:
                st.error(
                    "Usuário ou senha inválidos! Já é cadastrado em nosso sistema? Se não, cadastre-se!")
        except Exception as e:
            st.error(f"Erro ao conectar ao banco de dados: {e}")
        finally:
            session.close()

    if register_button:
        st.session_state["show_register"] = True
        st.rerun()


# Página de cadastro
def register():
    st.title("Cadastro do Paciente")

    if 'imagem_bytes' not in st.session_state:
        st.session_state.imagem_bytes = None

    with st.form("Cadastro do Paciente"):
        nome = st.text_input("Nome")
        senha = st.text_input("Senha", type="password")
        data_nascimento = st.text_input("Data de Nascimento (DD/MM/AAAA)")
        endereco = st.text_input("Endereço")
        cep = st.text_input("CEP")
        telefone = st.text_input("Telefone")
        tempo_lesao = st.text_input("Tempo com a Lesão")
        historico_diabetes = st.radio(
            "Histórico de Diabetes na família:", ["Sim", "Não"])
        historico_cancer = st.radio(
            "Histórico de Câncer na família:", ["Sim", "Não"])
        anti_inflamatorio = st.radio(
            "Anti-inflamatório sem efeito:", ["Sim", "Não"])
        imagem_lesao = st.file_uploader(
            "Imagem da Lesão", type=["jpg", "png", "jpeg"])

        if imagem_lesao is not None:
            st.session_state.imagem_bytes = imagem_lesao.read()
            st.image(st.session_state.imagem_bytes,
                     caption="Preview da imagem")

        submit = st.form_submit_button("Cadastrar")
        if submit:
            if not nome or not senha or not data_nascimento or not endereco or not cep or not telefone or not tempo_lesao or not st.session_state.imagem_bytes:
                st.error("Por favor, preencha todos os campos obrigatórios.")
                return

            try:
                datetime.strptime(data_nascimento, "%d/%m/%Y")
            except ValueError:
                st.error("Data de nascimento inválida. Use o formato DD/MM/AAAA.")
                return

            # Gera o hash da senha
            hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
            session = Session()

            try:
                query = text("""
                INSERT INTO PACIENTE
                (NOME, SENHA, DATA_DE_NASCIMENTO, ENDERECO, CEP, TELEFONE,
                TEMPO_COM_A_LESAO, HISTORICO_DIABETES, HISTORICO_CANCER,
                ANTI_INFLAMATORIO_SEM_EFEITO, IMAGEM_LESAO)
                VALUES
                (:nome, :senha, :data_nascimento, :endereco, :cep, :telefone,
                :tempo_lesao, :historico_diabetes, :historico_cancer,
                :anti_inflamatorio, :imagem_lesao)
                """)
                session.execute(query, {
                    "nome": nome,
                    "senha": hashed_password,  # Armazena o hash como bytes
                    "data_nascimento": data_nascimento,
                    "endereco": endereco,
                    "cep": cep,
                    "telefone": telefone,
                    "tempo_lesao": tempo_lesao,
                    "historico_diabetes": historico_diabetes == "Sim",
                    "historico_cancer": historico_cancer == "Sim",
                    "anti_inflamatorio": anti_inflamatorio == "Sim",
                    "imagem_lesao": st.session_state.imagem_bytes
                })
                session.commit()
                st.success("Paciente cadastrado com sucesso!")
                time.sleep(2)
                st.session_state["show_register"] = False
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao inserir dados no banco: {e}")
                session.rollback()
            finally:
                session.close()


# Página principal da área do paciente
# Página principal da área do paciente
def patient_area():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        if "show_register" in st.session_state and st.session_state["show_register"]:
            register()
        else:
            patient_login()
    else:
        st.subheader(f"Bem-vindo, {st.session_state['user']['nome']}!")
        st.write("Faça upload de uma imagem para análise:")

        # Garantir que a variável de imagem esteja no session state
        if "image" not in st.session_state:
            st.session_state["image"] = None
        if "resultado" not in st.session_state:
            st.session_state["resultado"] = None

        # Exibir o upload de imagem logo após o login
        uploaded_image = st.file_uploader(
            "Escolha uma imagem", type=["jpg", "jpeg", "png"])

        if uploaded_image is not None:
            try:
                # Processar a imagem enviada
                file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
                st.session_state["image"] = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                resultado = classify_image(st.session_state["image"])
                st.session_state["resultado"] = resultado
            except Exception as e:
                st.error(f"Erro ao processar a imagem: {e}")

        if st.session_state["image"] is not None:
            st.image(st.session_state["image"], channels="BGR", width=300)

            if st.button("Limpar"):
                st.session_state["image"] = None
                st.session_state["resultado"] = None
                st.rerun()

        if st.session_state["image"] is None:
            st.info("Faça o upload de uma imagem de alta qualidade da lesão para classificá-la.")


# Executar o aplicativo
if "show_register" not in st.session_state:
    st.session_state["show_register"] = False
