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


def classify_image(image):
    """
    Classifies the given image to detect leishmaniasis lesions.

    Args:
        image (numpy.ndarray): Loaded image to classify.

    Returns:
        torch.Tensor: Predicted probabilities for each class.

    """
    # Preprocess the image
    image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    img = transform(image).unsqueeze(0)

    # Perform prediction with the model
    with torch.no_grad():
        outputs = model(img)
        probability = F.softmax(outputs, dim=1)
        max_probability = torch.max(probability).item()
        predicted_class = torch.argmax(probability).item()

    # Check if confidence is high enough for classification
    if max_probability >= 0.7:
        formatted_probability = max_probability * 100
        if predicted_class == 0:
            st.write(
                f'A lesão aparenta ser causada por carcinoma basocelular com uma probabilidade de: '
                f'{formatted_probability:.2f}%'
            )
            st.write(
                'Consulte hospitais especializados mais próximos para uma avaliação médica!'
            )
        elif predicted_class == 1:
            st.write(
                f'A lesão aparenta ser causada por diabetes com uma probabilidade de: '
                f'{formatted_probability:.2f}%'
            )
            st.write(
                'Consulte hospitais especializados mais próximos para uma avaliação médica!'
            )
        elif predicted_class == 2:
            st.write(
                f'A lesão aparenta ser causada por leishmaniose com uma probabilidade de: '
                f'{formatted_probability:.2f}%'
            )
            st.write(
                'Consulte hospitais especializados mais próximos para uma avaliação médica!'
            )
        elif predicted_class == 3:
            st.write(
                'Você não aparenta ter uma lesão, tem certeza que subiu uma foto de qualidade e com uma lesão cutânea ?'
            )
        elif predicted_class == 4:
            st.write(
                f'A lesão aparenta ser causada por pioderma com uma probabilidade de: '
                f'{formatted_probability:.2f}%'
            )
            st.write(
                'Consulte hospitais especializados mais próximos para uma avaliação médica!'
            )
        elif predicted_class == 5:
            st.write(
                f'A lesão aparenta ser causada por doença venosa com uma probabilidade de: '
                f'{formatted_probability:.2f}%'
            )
            st.write(
                'Consulte hospitais especializados mais próximos para uma avaliação médica!'
            )
    else:
        st.write(
            "Confiança insuficiente para uma classificação precisa. "
            "Tente uma imagem mais clara."
        )

    return probability
