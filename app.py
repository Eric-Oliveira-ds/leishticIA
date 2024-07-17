import streamlit as st
from utils.classifier import classificar_imagem

# Cabeçalho
image = r"images\2020-10-17.jpg"
st.sidebar.image(image, use_column_width=True)
st.title('Triagem de Leishmaniose e Tuberculose Cutânea com apoio da IA')

# Navegação
st.sidebar.title("Navegação")
page = st.sidebar.selectbox("Selecione a página", [
                            "Sobre as Doenças", "Classificação de Imagens"])

# Aba Lateral
st.sidebar.title("Clínicas especializadas")
st.sidebar.write("""
- [Hospital Universitário Dr. Edgar Santos](https://www.google.com/search?sca_esv=54722a0b5ffac30e&rlz=1C1ONGR_pt-PTBR1070BR1070&sxsrf=ADLYWILzrXmzgwQ_iQvrdT8E3kk5yER1Ig:1720656569393&q=Hospital+Universit%C3%A1rio+Dr.+Edgard+Santos&spell=1&sa=X&ved=2ahUKEwiFmeWc2Z2HAxUavJUCHTnRCIEQBSgAegQIDxAB&biw=1920&bih=911&dpr=1#)
""")

# Adicionar imagem na barra lateral
image = r"images/streamlit_header_pil.png"
st.sidebar.image(image, use_column_width=True)
st.sidebar.markdown("---")
st.sidebar.markdown("Autor: Eric Oliveira")
st.sidebar.markdown("**Copyright © 2024**")
st.sidebar.markdown(
    "[LinkedIn](https://www.linkedin.com/in/eric-oliveira-ds/)")

# Conteúdo da Página
if page == "Sobre as Doenças":
    st.header('Sobre as Doenças')
    st.subheader('Leishmaniose')
    st.write("""
    - **Descrição**: A leishmaniose é uma doença parasitária transmitida pela picada de flebotomíneos infectados. A forma cutânea da leishmaniose provoca feridas na pele, que podem ser desfigurantes.
    - **Causas**: É causada por protozoários do gênero Leishmania.
    - **Número de casos no Brasil**: Cerca de 3.500 casos são registrados anualmente, com a maioria dos casos concentrados nas regiões Norte, Nordeste e Centro-Oeste.
    """)

    st.subheader('Tuberculose Cutânea')
    st.write("""
    - **Descrição**: A tuberculose cutânea é uma forma rara de tuberculose que afeta a pele. Pode manifestar-se de várias maneiras, incluindo lesões verrucosas e úlceras crônicas.
    - **Causas**: É causada pela bactéria Mycobacterium tuberculosis.
    - **Número de casos no Brasil**: Embora mais rara que outras formas de tuberculose, a tuberculose cutânea ainda é relevante em áreas endêmicas de tuberculose.
    """)
elif page == "Classificação de Imagens":
    st.header('Classificação de Imagens')
    st.write(
        'Faça upload de uma imagem para classificação ou tire uma foto diretamente da sua câmera:')

    # Upload de arquivo
    uploaded_file = st.file_uploader(
        "Escolha uma imagem...", type=["jpg", "jpeg", "png"])

    # Captura de imagem com a câmera
    captured_image = st.camera_input(
        "Tire uma foto, por favor certifique-se de quê está em um ambiente iluminado que facilite a captura da foto com qualidade !")

    if uploaded_file is not None or captured_image is not None:
        if uploaded_file is not None:
            image = uploaded_file
        else:
            image = captured_image

        st.image(image, use_column_width=True)
        resultado = classificar_imagem(image)
        st.write(f'Resultado da classificação: {resultado}')
