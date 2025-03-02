import os
import bcrypt
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import time

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


# Controla o fluxo entre login e cadastro
def medico_area():
    if "medico_logged_in" not in st.session_state or not st.session_state["medico_logged_in"]:
        if "show_register" in st.session_state and st.session_state["show_register"]:
            medico_register()
        else:
            medico_login()
    else:
        st.success(f"Bem-vindo, Dr(a). {st.session_state['medico_user']['nome']}!")
        st.write("Agora você pode melhorar a qualidade de vida dos pacientes!")
