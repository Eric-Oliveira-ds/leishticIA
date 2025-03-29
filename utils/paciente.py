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
import folium
from streamlit_folium import st_folium
import googlemaps

load_dotenv()

# Obtendo os valores das variáveis de ambiente
host = os.getenv('DB_HOST', 'localhost')
port = os.getenv('DB_PORT', 5432)
database = os.getenv('DB_DATABASE', 'LeisHticIA_gold')
user = os.getenv('DB_USER', 'postgres')
password = os.environ.get("PG_PASSWORD")

# Configuração da API do Google Maps
gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))

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


# Funções auxiliares locais
def get_location_from_address(address):
    """Converte um endereço em coordenadas geográficas (latitude, longitude)."""
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        location = geocode_result[0]['geometry']['location']
        return location['lat'], location['lng']
    return None, None


days_translation = {
    "Monday": "Segunda-feira",
    "Tuesday": "Terça-feira",
    "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira",
    "Friday": "Sexta-feira",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}


def format_hours(hours):
    """Formata o horário no padrão brasileiro (24 horas)."""
    hours = hours.replace(" AM", "").replace(" PM", "")
    if "PM" in hours:
        parts = hours.split(" – ")
        if len(parts) == 2:
            start, end = parts
            start = str(int(start.split(":")[0]) + 12) + ":" + start.split(":")[1]
            end = str(int(end.split(":")[0]) + 12) + ":" + end.split(":")[1]
            return f"{start} – {end}"
    return hours


def find_nearby_hospitals(latitude, longitude, radius=5000):
    """Encontra hospitais próximos à localização fornecida, especializados em feridas e edemas."""
    # Palavras-chave para filtrar hospitais especializados
    keyword = "tratamento de feridas, tratamento de edemas, tratamento de cancer, tratamento de diabetes"

    # Realiza a busca na API do Google Places
    places_result = gmaps.places_nearby(
        location=(latitude, longitude),
        radius=radius,
        type='hospital',
        keyword=keyword  # Filtra por palavras-chave
    )

    hospitals = []
    for place in places_result.get('results', []):
        # Obtém detalhes adicionais do lugar, incluindo o horário de funcionamento
        place_details = gmaps.place(place['place_id'], fields=["name", "vicinity", "rating", "geometry", "opening_hours"])

        name = place_details['result'].get('name', 'Nome não disponível')
        address = place_details['result'].get('vicinity', 'Endereço não disponível')
        rating = place_details['result'].get('rating', 'N/A')
        location = place_details['result']['geometry']['location']
        
        # Obtém o horário de funcionamento
        opening_hours = place_details['result'].get('opening_hours', {})
        if opening_hours:
            hours = opening_hours.get('weekday_text', ['Horário não disponível'])
            # Traduz os dias da semana e formata o horário
            hours_pt_br = []
            for day in hours:
                if ":" in day:  # Verifica se é um dia com horário
                    day_name, time = day.split(":", 1)
                    day_name = days_translation.get(day_name.strip(), day_name.strip())
                    time = format_hours(time.strip())
                    hours_pt_br.append(f"{day_name}: {time}")
                else:
                    hours_pt_br.append(day)
        else:
            hours_pt_br = ['Horário não disponível']

        hospitals.append((name, address, rating, location['lat'], location['lng'], hours_pt_br))
    
    return hospitals


# Página de login para o paciente
def patient_login():
    """
    Controla o fluxo de login/cadastro do paciente.

    Se o paciente estiver logado, exibe mensagem de boas-vindas e permite o cadastro de 
    les es. Caso contr rio, verifica se o bot o de cadastro foi apertado e, se sim, chama a 
    fun o de cadastro, sen o, chama a fun o de login.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """

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
    """
    Fun o que permite o cadastro de pacientes.

    Essa fun o   chamada quando o paciente clica no bot o "Cadastrar-se" na p gina de login.
    Ela exibe um formul rio para o paciente preencher suas informa es.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
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
            hashed_password = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt(12))
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
def patient_area():
    """
    Página principal da área do paciente.

    Essa página permite que o paciente faça upload de uma imagem para análise e visualize
    os resultados. Além disso, também permite que o paciente informe seu endereço e visualize
    hospitais especializados próximos.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
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

        # Coletar localização do paciente
        st.subheader("Localização do Paciente")
        patient_address = st.text_input("Digite seu endereço para encontrar hospitais próximos:")

        if patient_address:
            latitude, longitude = get_location_from_address(patient_address)
            if latitude and longitude:
                st.write(f"Coordenadas: Latitude {latitude}, Longitude {longitude}")
                hospitals = find_nearby_hospitals(latitude, longitude)
                if hospitals:
                    st.subheader("Hospitais Especializados Próximos:")

                    # Criar um mapa centrado na localização do paciente
                    m = folium.Map(location=[latitude, longitude], zoom_start=13)

                    # Adicionar marcador para a localização do paciente
                    folium.Marker(
                        location=[latitude, longitude],
                        popup="Sua Localização",
                        icon=folium.Icon(color="blue")
                    ).add_to(m)

                    # Adicionar marcadores para os hospitais
                    for hospital in hospitals:
                        folium.Marker(
                            location=[hospital[3], hospital[4]],
                            popup=f"{hospital[0]} - Avaliação: {hospital[2]}",
                            icon=folium.Icon(color="red")
                        ).add_to(m)

                    # Exibir o mapa no Streamlit
                    st_folium(m, width=700, height=500)

                    # Exibir detalhes dos hospitais
                    for hospital in hospitals:
                        st.write(f"Nome: {hospital[0]}")
                        st.write(f"Endereço: {hospital[1]}")
                        st.write(f"Avaliação: {hospital[2]}")
                        st.write("Horário de Funcionamento:")
                        for day in hospital[5]:  # hospital[5] contém o horário de funcionamento
                            st.write(f"- {day}")
                        st.write("---")
                else:
                    st.warning("Nenhum hospital especializado encontrado nas proximidades.")
            else:
                st.error("Não foi possível encontrar a localização. Verifique o endereço e tente novamente.")


# Executar o aplicativo
if "show_register" not in st.session_state:
    st.session_state["show_register"] = False
