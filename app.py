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
                                "Sobre as doenças",
                                "Área do paciente",
                                "Área do ACS",
                                "Área do médico"])

    # Aba Lateral
    st.sidebar.title("Clínicas especializadas")
    st.sidebar.write("""
    - Em desenvolvimento...
    """)

    # Adicionar barra lateral
    st.sidebar.markdown("---")
    st.sidebar.markdown("Autor: Eric Oliveira")
    st.sidebar.markdown("**Copyright © 2024**")
    st.sidebar.markdown(
        "[LinkedIn](https://www.linkedin.com/in/eric-oliveira-ds/)")

    # Conteúdo da Página
    if page == "Sobre as doenças":
        st.header('LeisHtic.IA')
        st.subheader('A LeisHtic.IA é um projeto de pesquisa que utiliza de IA para classificar imagens cutaneas de leishmaniasis, pyoderma, diabetes, venosas com o objetivo de ajudar a diagnosticar e tratar essas doenças de forma mais eficiente.')
        # Diabetic Wounds
        st.write("""
                - **Descrição**: Feridas diabéticas são complicações comuns em pacientes com diabetes mal controlado. Elas podem levar a infecções graves e até amputações.
                - **Causas**: Ocorrem devido a má circulação sanguínea e danos nos nervos periféricos, comuns em pessoas com diabetes.
                - **Número de casos no Brasil**: Estima-se que mais de 80.000 amputações sejam realizadas anualmente no Brasil devido a complicações do diabetes, incluindo feridas diabéticas.
                """)

        # Leishmaniose
        st.write("""
                - **Descrição**: A leishmaniose é uma doença parasitária transmitida pela picada de flebotomíneos infectados. A forma cutânea da leishmaniose provoca feridas na pele, que podem ser desfigurantes.
                - **Causas**: É causada por protozoários do gênero Leishmania.
                - **Número de casos no Brasil**: Cerca de 3.500 casos são registrados anualmente, com a maioria dos casos concentrados nas regiões Norte, Nordeste e Centro-Oeste.
                """)

        # Pyoderma
        st.write("""
                - **Descrição**: O pioderma é uma infecção bacteriana da pele, frequentemente causada por bactérias como Staphylococcus aureus e Streptococcus pyogenes. 
                - **Causas**: A infecção pode ser resultado de feridas abertas, condições de higiene inadequada ou imunidade comprometida.
                - **Número de casos no Brasil**: Não há estimativas exatas, mas infecções bacterianas da pele são muito comuns em áreas tropicais e úmidas, afetando milhares de pessoas anualmente.
                """)

        # Venous Ulcers
        st.write("""
                - **Descrição**: As úlceras venosas são feridas crônicas que ocorrem geralmente nas pernas, devido a problemas na circulação sanguínea. Elas são dolorosas e de difícil cicatrização.
                - **Causas**: Resultam de insuficiência venosa crônica, onde as válvulas nas veias não funcionam adequadamente, causando acúmulo de sangue.
                - **Número de casos no Brasil**: Afetam cerca de 1% da população adulta e até 3% dos idosos, especialmente em regiões urbanas.
                """)

    # Adicionar barra lateral
    elif page == "Área do paciente":
        st.header('Área do paciente')
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
