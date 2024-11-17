import streamlit as st
import cv2
import numpy as np
from utils.classifier import classify_image


def main():
    # Cabeçalho
    image_path = r"images/LeisHticIA.png"
    st.sidebar.image(image_path, use_column_width=True)
    st.title('Identificação de lesões causadas por doenças com apoio da IA')

    # Navegação
    st.sidebar.title("Navegação")
    page = st.sidebar.selectbox("Selecione a página", [
                                "Sobre as doenças", "Classificação de imagens"])

    # Aba Lateral
    st.sidebar.title("Clínicas especializadas")
    st.sidebar.write("""
    - [Hospital Universitário Dr. Edgar Santos](https://www.google.com/search?sca_esv=54722a0b5ffac30e&rlz=1C1ONGR_pt-PTBR1070BR1070&sxsrf=ADLYWILzrXmzgwQ_iQvrdT8E3kk5yER1Ig:1720656569393&q=Hospital+Universit%C3%A1rio+Dr.+Edgard+Santos&spell=1&sa=X&ved=2ahUKEwiFmeWc2Z2HAxUavJUCHTnRCIEQBSgAegQIDxAB&biw=1920&bih=911&dpr=1#)
    """)

    # Adicionar barra lateral
    st.sidebar.markdown("---")
    st.sidebar.markdown("Autor: Eric Oliveira")
    st.sidebar.markdown("**Copyright © 2024**")
    st.sidebar.markdown(
        "[LinkedIn](https://www.linkedin.com/in/eric-oliveira-ds/)")

    # Conteúdo da Página
    if page == "Sobre as doenças":
        st.header('Sobre as doenças')
        st.subheader('Em desenvolvimento')
        st.write("""
                Em desenvolvimento com novas doenças e uma nova base de dados. Por favor aguarde.
        """)

    elif page == "Classificação de imagens":
        st.header('Classificação de imagens')
        st.write(
            'Faça upload de uma imagem da sua galeria para classificação:')

        # Variável para armazenar a imagem e o resultado da classificação no estado da sessão
        if 'image' not in st.session_state:
            st.session_state['image'] = None
        if 'resultado' not in st.session_state:
            st.session_state['resultado'] = None

        upload_image_button = st.button('Fazer Upload de Imagem')

        # Upload de arquivo
        if upload_image_button:
            st.session_state['capturing'] = False
            st.session_state['uploading'] = True

        if st.session_state.get('uploading', False):
            uploaded_file = st.file_uploader(
                "Escolha uma imagem...", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                st.session_state['image'] = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                st.session_state['resultado'] = classify_image(st.session_state['image'])
                st.session_state['uploading'] = False

        # Botão para limpar imagem e resultado
        if st.session_state['image'] is not None:
            st.image(st.session_state['image'], channels="BGR", width=300)
            if st.button('Limpar'):
                st.session_state['image'] = None
                st.session_state['resultado'] = None
                st.rerun()
        else:
            st.info("""Faça o upload de uma imagem de alta qualidade da lesão para classifica-la.""")

        st.markdown("""
        # Isenção de responsabilidade

        Esta aplicação utiliza um modelo de inteligência artificial para classificar doenças a partir de imagens. **Os resultados fornecidos por esta aplicação são apenas para fins informativos e não substituem uma consulta médica profissional.**

        Recomendamos fortemente que você procure um médico para um diagnóstico preciso e para o tratamento adequado.

        **Ao utilizar esta aplicação, você concorda que compreende os riscos e limitações e que não responsabilizará os desenvolvedores por qualquer decisão tomada com base nos resultados fornecidos por esta ferramenta.**
        """)


if __name__ == "__main__":
    main()
