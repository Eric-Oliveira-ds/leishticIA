import cv2
import streamlit as st
import numpy as np
from keras.models import model_from_json, Sequential
from keras.saving import register_keras_serializable

# Registrar a classe Sequential
register_keras_serializable()(Sequential)

# Carregar o modelo do arquivo JSON
with open(r'model\model.json', 'r') as json_file:
    loaded_model_json = json_file.read()
    json_file.close()

loaded_model = model_from_json(loaded_model_json)
loaded_model.load_weights(r'model\model.h5')
loaded_model.compile(loss='categorical_crossentropy', optimizer='Adam', metrics=['accuracy'])
print("A IA está trabalhando...")


def classificar_imagem(image):
    img = cv2.resize(image, (64, 64))
    img = img / 255
    img = img.reshape(-1, 64, 64, 3)
    previsao = loaded_model.predict(img)
    probabilidade = np.max(previsao)
    classe_prevista = np.argmax(previsao)

    probabilidade_formatada = np.round(probabilidade * 100, 2)  # Converter para porcentagem e arredondar para 2 casas decimais

    if classe_prevista == 0:
        st.write(f'A lesão se parece com leishmaniose com probabilidade de: {probabilidade_formatada}%')
    else:
        st.write(f'A lesão se parece com tuberculose cutânea com probabilidade de: {probabilidade_formatada}%')

    st.write(f'Procure hospitais especializados mais próximos!')

    return previsao
