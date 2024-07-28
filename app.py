import streamlit as st
import cv2
import numpy as np
from utils.classifier import classificar_imagem


def main():
    # Cabeçalho
    image_path = r"images\2020-10-17.jpg"
    st.sidebar.image(image_path, use_column_width=True)
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
    sidebar_image_path = r"images/streamlit_header_pil.png"
    st.sidebar.image(sidebar_image_path, use_column_width=True)
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

        # Variável para armazenar a imagem e o resultado da classificação no estado da sessão
        if 'image' not in st.session_state:
            st.session_state['image'] = None
        if 'resultado' not in st.session_state:
            st.session_state['resultado'] = None

        # Botões para captura de imagem e upload
        capture_image_button = st.button('Tirar Foto com Câmera')
        upload_image_button = st.button('Fazer Upload de Imagem')

        # Captura de imagem com a câmera
        if capture_image_button:
            st.session_state['capturing'] = True
            st.session_state['uploading'] = False

        # Upload de arquivo
        if upload_image_button:
            st.session_state['capturing'] = False
            st.session_state['uploading'] = True

        if st.session_state.get('capturing', False):
            captured_image = st.camera_input("Tire uma foto")
            if captured_image is not None:
                file_bytes = np.asarray(bytearray(captured_image.read()), dtype=np.uint8)
                st.session_state['image'] = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                st.session_state['resultado'] = classificar_imagem(st.session_state['image'])
                st.session_state['capturing'] = False

        if st.session_state.get('uploading', False):
            uploaded_file = st.file_uploader(
                "Escolha uma imagem...", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                st.session_state['image'] = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                st.session_state['resultado'] = classificar_imagem(st.session_state['image'])
                st.session_state['uploading'] = False

        # Exibir imagem e resultado da classificação, se disponíveis
        if st.session_state['image'] is not None:
            st.image(st.session_state['image'], channels="BGR", use_column_width=True)
        else:
            st.info("Tire uma foto ou faça upload de uma imagem para classificação.")
        # Exibir a isenção de responsabilidade no início da aplicação
        st.markdown("""
        # Isenção de Responsabilidade

        Esta aplicação utiliza um modelo de inteligência artificial para classificar doenças a partir de imagens. **Os resultados fornecidos por esta aplicação são apenas para fins informativos e não substituem uma consulta médica profissional.**

        Recomendamos fortemente que você procure um médico para um diagnóstico preciso e para o tratamento adequado.

        **Ao utilizar esta aplicação, você concorda que compreende os riscos e limitações e que não responsabilizará os desenvolvedores por qualquer decisão tomada com base nos resultados fornecidos por esta ferramenta.**
        """)


if __name__ == "__main__":
    main()
