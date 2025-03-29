import streamlit as st
import os
from utils.paciente import patient_area
from utils.agente_saude import acs_area
from utils.medico import medico_area


def disclaimer():
    """Exibe a isenção de responsabilidade."""
    st.markdown("""
    ## Isenção de responsabilidade

    Esta aplicação utiliza um modelo de inteligência artificial para classificar doenças a partir de imagens.  
    **Os resultados fornecidos são apenas para fins informativos e não substituem uma consulta médica profissional.**

    Recomendamos fortemente que você procure um médico para um diagnóstico preciso e para o tratamento adequado.

    **Ao utilizar esta aplicação, você compreende os riscos e limitações e não responsabilizará os desenvolvedores por qualquer decisão tomada com base nos resultados fornecidos.**
    """)


def main():
    """Função principal do aplicativo Streamlit."""
    # Carregar imagem do cabeçalho
    image_path = r"images/LeisHticIA.png"
    if os.path.exists(image_path):
        st.sidebar.image(image_path, use_container_width=True)

    # Título
    st.title('Identificação de lesões cutâneas causadas por doenças com apoio da IA')

    # Navegação
    st.sidebar.title("Navegação")
    page = st.sidebar.selectbox("Selecione a página", [
        "Sobre as doenças",
        "Área do paciente",
        "Área do ACS",
        "Área do médico"
    ])

    # Rodapé na barra lateral
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Autor: Eric Oliveira**")
    st.sidebar.markdown("© 2024")
    st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/eric-oliveira-ds/)")

    # Conteúdo da Página
    if page == "Sobre as doenças":
        st.header('LeisHtic.IA')
        st.subheader('Classificação de lesões cutâneas com IA')

        doencas_info = {
            "Feridas Diabéticas": {
                "Descrição": "Feridas comuns em diabéticos mal controlados, podendo levar a infecções graves e amputações.",
                "Causas": "Má circulação sanguínea e danos nos nervos periféricos.",
                "Casos no Brasil": "Mais de 80.000 amputações anuais relacionadas ao diabetes."
            },
            "Leishmaniose": {
                "Descrição": "Doença parasitária transmitida por picada de flebotomíneos infectados, causando feridas na pele.",
                "Causas": "Protozoários do gênero Leishmania.",
                "Casos no Brasil": "Cerca de 3.500 casos anuais, principalmente no Norte, Nordeste e Centro-Oeste."
            },
            "Pioderma": {
                "Descrição": "Infecção bacteriana da pele causada por bactérias como Staphylococcus aureus.",
                "Causas": "Feridas abertas, higiene inadequada ou imunidade comprometida.",
                "Casos no Brasil": "Muito comum em áreas tropicais e úmidas."
            },
            "Úlceras Venosas": {
                "Descrição": "Feridas crônicas nas pernas devido a problemas circulatórios.",
                "Causas": "Insuficiência venosa crônica e acúmulo de sangue.",
                "Casos no Brasil": "Afetam cerca de 1% da população adulta e até 3% dos idosos."
            },
            "Carcinoma Basocelular": {
                "Descrição": "Tipo mais comum de câncer de pele, com crescimento anormal de células da epiderme.",
                "Causas": "Exposição à radiação UV, idade avançada e predisposição genética.",
                "Casos no Brasil": "Cerca de 176 mil novos casos anuais de câncer de pele não melanoma."
            }
        }

        for doenca, info in doencas_info.items():
            st.write(f"### {doenca}")
            for key, value in info.items():
                st.write(f"- **{key}**: {value}")

    elif page == "Área do paciente":
        patient_area()
        disclaimer()

    elif page == "Área do ACS":
        acs_area()
        disclaimer()

    elif page == "Área do médico":
        medico_area()


if __name__ == "__main__":
    main()
