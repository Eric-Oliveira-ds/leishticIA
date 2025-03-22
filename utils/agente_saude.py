import os
import bcrypt
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import time
from utils.paciente import register

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
    Retorna o engine do SQLAlchemy para conex o com o banco de dados.
    
    Returns
    -------
    engine : sqlalchemy.engine.Engine
        O engine do SQLAlchemy para conex o com o banco de dados.
    """
    return create_engine(DATABASE_URL)


# Inicializando o SessionMaker
engine = get_engine()
Session = sessionmaker(bind=engine)

# Página de login/cadastro do ACS


def acs_login():
    """
    Handles the login process for Community Health Agents (ACS).

    This function displays a login interface for ACS, allowing them to enter their
    username and password. If the login button is clicked, it verifies the credentials
    against the database. If the credentials are valid, the session state is updated
    to reflect that the ACS is logged in. If the credentials are invalid, an error message
    is shown. It also provides an option to navigate to the registration page if the
    ACS does not have an account.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    st.title("Login do ACS")
    username = st.text_input("Nome")
    password = st.text_input("Senha", type="password")
    login_button = st.button("Entrar")
    register_button = st.button("Cadastrar-se")

    if login_button:
        session = Session()
        try:
            query = text("SELECT * FROM AGENTE_COMUNITARIO WHERE NOME = :username")
            result = session.execute(
                query, {"username": username}).mappings().fetchone()

            if result and bcrypt.checkpw(password.encode('utf-8'), bytes(result["senha"])):
                st.success("Login realizado com sucesso!")
                st.session_state["acs_logged_in"] = True
                st.session_state["acs_user"] = result
            else:
                st.error("Usuário ou senha inválidos!")
        except Exception as e:
            st.error(f"Erro ao conectar ao banco: {e}")
        finally:
            session.close()

    if register_button:
        st.session_state["show_register"] = True
        st.rerun()

# Página de cadastro do ACS


def acs_register():
    """
    Função para cadastro de um novo ACS.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    st.title("Cadastro do ACS")
    nome = st.text_input("Nome")
    senha = st.text_input("Senha", type="password")
    endereco = st.text_input("Endereço")
    cep = st.text_input("CEP")
    area = st.text_input("Área")
    micro_area = st.number_input("Micro-área", min_value=1, step=1)
    submit = st.button("Cadastrar")

    if submit:
        if not nome or not area or not senha:
            st.error("Por favor, preencha todos os campos.")
            return
        hashed_password = bcrypt.hashpw(
            senha.encode('utf-8'), bcrypt.gensalt(12))
        session = Session()
        try:
            query = text("""
                INSERT INTO AGENTE_COMUNITARIO (NOME, SENHA, ENDERECO, CEP, AREA, MICRO_AREA)
                VALUES (:nome, :senha, :endereco, :cep, :area, :micro_area)
            """)
            session.execute(query, {
                "nome": nome,
                "senha": hashed_password,
                "endereco": endereco,
                "cep": cep,
                "area": area,
                "micro_area": micro_area
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


def acs_area():
    """
    Controla o fluxo de login/cadastro de Agentes Comunitários de Saúde.

    Se o ACS estiver logado, exibe mensagem de boas-vindas e permite o cadastro de pacientes.
    Caso contrário, verifica se o botão de cadastro foi apertado e, se sim, chama a função
    de cadastro, senão, chama a função de login.
    """
    if "acs_logged_in" not in st.session_state or not st.session_state["acs_logged_in"]:
        if "show_register" in st.session_state and st.session_state["show_register"]:
            acs_register()
        else:
            acs_login()
    else:
        st.success(f"Bem-vindo, {st.session_state['acs_user']['nome']}!")
        st.write("Agora você pode cadastrar pacientes.")
        register()
