import bcrypt
import streamlit as st
from dotenv import load_dotenv
import cv2
import numpy as np
from utils.classifier import classify_image

load_dotenv()
# Conectar ao banco de dados
st.cache_resource


def get_connection():
    """
    Singleton para criar uma conexão com o banco de dados PostgreSQL.
    """
    return st.connection("postgres", type="sql")


# Página de login para o paciente
def patient_login():
    st.subheader("Login do Paciente")
    username = st.text_input("Nome de Usuário")
    password = st.text_input("Senha", type="password")
    login_button = st.button("Entrar")
    register_button = st.button("Cadastrar-se")

    if login_button:
        connection = get_connection()
        try:
            query = f"SELECT * FROM PACIENTE WHERE NOME = '{username}'"
            user = connection.query(query, ttl="10m").fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'), user["senha"]):
                st.success("Login realizado com sucesso!")
                st.session_state["logged_in"] = True
                st.session_state["user"] = user
            else:
                st.error(
                    "Usuário ou senha inválidos! Já é cadastrado em nosso sistema? Se não, cadastre-se!")
        except Exception as e:
            st.error(f"Erro ao conectar ao banco de dados: {e}")

    if register_button:
        register()


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
        connection = get_connection()

        if submit:
            if not all([nome, senha, data_nascimento, endereco, cep, telefone, tempo_lesao, st.session_state.imagem_bytes]):
                st.error("Por favor, preencha todos os campos obrigatórios.")
                return

            hashed_password = bcrypt.hashpw(
                senha.encode('utf-8'), bcrypt.gensalt())
            try:
                query = """
                INSERT INTO PACIENTE
                (NOME, SENHA, DATA_DE_NASCIMENTO, ENDERECO, CEP, TELEFONE,
                TEMPO_COM_A_LESAO, HISTORICO_DIABETES, HISTORICO_CANCER,
                ANTI_INFLAMATORIO_SEM_EFEITO, IMAGEM_LESAO)
                VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                connection.execute(query, (
                    nome,
                    hashed_password,
                    data_nascimento,
                    endereco,
                    cep,
                    telefone,
                    tempo_lesao,
                    historico_diabetes == "Sim",
                    historico_cancer == "Sim",
                    anti_inflamatorio == "Sim",
                    st.session_state.imagem_bytes
                ))
                st.success("Paciente cadastrado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao inserir dados no banco: {str(e)}")


# Página principal da área do paciente
def patient_area():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        patient_login()
    else:
        st.subheader(f"Bem-vindo, {st.session_state['user']['nome']}!")
        st.write("Faça upload de uma imagem para análise:")

        if "image" not in st.session_state:
            st.session_state["image"] = None
        if "resultado" not in st.session_state:
            st.session_state["resultado"] = None

        uploaded_image = st.file_uploader(
            "Escolha uma imagem", type=["jpg", "jpeg", "png"])

        if uploaded_image is not None:
            file_bytes = np.asarray(
                bytearray(uploaded_image.read()), dtype=np.uint8)
            st.session_state["image"] = cv2.imdecode(
                file_bytes, cv2.IMREAD_COLOR)

            st.write("Analisando a imagem...")
            try:
                resultado = classify_image(st.session_state["image"])
                st.session_state["resultado"] = resultado
                st.success(f"Resultado da Classificação: **{resultado}**")
            except Exception as e:
                st.error(f"Erro ao processar a imagem: {e}")

        if st.session_state["image"] is not None:
            st.image(st.session_state["image"], channels="BGR", width=300)
            if st.button("Limpar"):
                st.session_state["image"] = None
                st.session_state["resultado"] = None
                st.rerun()

        if st.session_state["image"] is None:
            st.info(
                "Faça o upload de uma imagem de alta qualidade da lesão para classificá-la.")
