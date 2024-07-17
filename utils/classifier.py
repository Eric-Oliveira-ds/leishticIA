import cv2
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
    prev = np.argmax(previsao, axis=1)

    if prev == 0:
        print('leishmaniose')
    else:
        print('tuberculose_cutanea')

    return previsao
