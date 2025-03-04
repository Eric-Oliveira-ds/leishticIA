import cv2
import streamlit as st
import torch
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image


@st.cache_resource(show_spinner=False)
def load_model():
    """
    Load a pre-trained AlexNet model and weights from a file.

    Returns:
        A pre-trained AlexNet model with 5 output classes, loaded from a file.
    """
    model = models.alexnet(weights='AlexNet_Weights.IMAGENET1K_V1')
    model.classifier[6] = torch.nn.Linear(4096, 6)
    model.load_state_dict(torch.load('models/alexnet_acc_0.74_num_classes6_weights.pth',
                                     weights_only=True,
                                     map_location=torch.device('cpu')))
    model.eval()

    return model


model = load_model()

# Define image transformations
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


# Classes do modelo
CLASSES = [
    "Carcinoma Basocelular",
    "Diabetes",
    "Leishmaniose",
    "Sem Lesão",
    "Pioderma",
    "Venosa"
]

MENSAGENS = [
    "A lesão aparenta ser causada por carcinoma basocelular.",
    "A lesão aparenta ser causada por diabetes.",
    "A lesão aparenta ser causada por leishmaniose.",
    "Você não aparenta ter uma lesão. Tem certeza que subiu uma foto de qualidade e com uma lesão cutânea?",
    "A lesão aparenta ser causada por pioderma.",
    "A lesão aparenta ser causada por doença venosa."
]


def classify_image(image):
    """Classifica a imagem e retorna a classe predita e sua probabilidade."""

    # Pré-processamento da imagem
    image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    img = transform(image).unsqueeze(0)

    # Predição
    with torch.no_grad():
        outputs = model(img)
        probabilities = F.softmax(outputs, dim=1)

    # Obter a classe com maior probabilidade
    max_probability, predicted_class = torch.max(probabilities, dim=1)
    max_probability = max_probability.item()
    predicted_class = predicted_class.item()

    # Exibir resultado
    if max_probability >= 0.7:
        st.write(f"{MENSAGENS[predicted_class]} Probabilidade: {max_probability * 100:.0f}%")
        if predicted_class != 5:
            st.write("Consulte hospitais especializados mais próximos para uma avaliação médica!")
    else:
        st.write("Confiança insuficiente para uma classificação precisa. Tente uma imagem mais clara.")

    return CLASSES[predicted_class], max_probability
