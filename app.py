import streamlit as st
from utils.paciente import patient_area
from utils.agente_saude import acs_area


def main():
    # Cabeçalho
    """
    Entry point for the Streamlit application.

    This function is the main entry point for the Streamlit application. It
    contains the code to create the user interface, including the navigation,
    the image upload and classification, and the display of the results.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    image_path = r"images/LeisHticIA.png"
    st.sidebar.image(image_path, use_container_width=True)
    st.title('Identificação de lesões causadas por doenças com apoio da IA')

    # Navegação
    st.sidebar.title("Navegação")
    page = st.sidebar.selectbox("Selecione a página", [
                                "Sobre as doenças",
                                "Área do paciente",
                                "Área do ACS",
                                "Área do médico"])

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
        # Carcinoma Basocelular
        st.write("""
                - **Descrição**: O carcinoma basocelular é o tipo mais comum de câncer de pele, caracterizado pelo crescimento anormal e descontrolado de células da camada basal da epiderme. Geralmente é localmente invasivo e raramente se espalha para outras partes do corpo.
                - **Causas**: Está relacionado principalmente à exposição prolongada e repetitiva à radiação ultravioleta (UV), seja por exposição ao sol ou ao uso de câmaras de bronzeamento artificial. Outros fatores de risco incluem idade avançada, pele clara e histórico familiar de câncer de pele.
                - **Número de casos no Brasil**: Estima-se que cerca de 176 mil novos casos de câncer de pele não melanoma, incluindo o carcinoma basocelular, sejam diagnosticados anualmente, representando aproximadamente 30% de todos os casos de câncer no país.
                """)

    # Adicionar barra lateral
    elif page == "Área do paciente":
        patient_area()

        st.markdown("""
                # Isenção de responsabilidade

                Esta aplicação utiliza um modelo de inteligência artificial para classificar doenças a partir de imagens. **Os resultados fornecidos por esta aplicação são apenas para fins informativos e não substituem uma consulta médica profissional.**

                Recomendamos fortemente que você procure um médico para um diagnóstico preciso e para o tratamento adequado.

                **Ao utilizar esta aplicação, você concorda que compreende os riscos e limitações e que não responsabilizará os desenvolvedores por qualquer decisão tomada com base nos resultados fornecidos por esta ferramenta.**
        """)

    # Adicionar barra lateral
    elif page == "Área do ACS":
        acs_area()

        st.markdown("""
                # Isenção de responsabilidade

                Esta aplicação utiliza um modelo de inteligência artificial para classificar doenças a partir de imagens. **Os resultados fornecidos por esta aplicação são apenas para fins informativos e não substituem uma consulta médica profissional.**

                Recomendamos fortemente que você procure um médico para um diagnóstico preciso e para o tratamento adequado.

                **Ao utilizar esta aplicação, você concorda que compreende os riscos e limitações e que não responsabilizará os desenvolvedores por qualquer decisão tomada com base nos resultados fornecidos por esta ferramenta.**
        """)


if __name__ == "__main__":
    main()
