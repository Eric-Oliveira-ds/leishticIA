import cv2
import streamlit as st
import torch
import torch.nn.functional as F
from torchvision import models, transforms
from PIL import Image

# Ensure the architecture matches your trained model
model = models.alexnet(pretrained=False)
model.classifier[6] = torch.nn.Linear(4096, 5)  # Update output layer to have 2 outputs

# Load the model weights
model.load_state_dict(torch.load('model/alexnet_acc81_weights.pth'))
model.eval()  # Set the model to evaluation mode

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
                f'A lesão aparenta ser leishmaniose com uma probabilidade de: '
                f'{formatted_probability:.2f}%'
            )
        else:
            st.write(
                f'A lesão aparenta ser pioderma com uma probabilidade de: '
                f'{formatted_probability:.2f}%'
            )
    else:
        st.write(
            "Confiança insuficiente para uma classificação precisa. "
            "Tente uma imagem mais clara."
        )

    st.write(
        'Consulte hospitais especializados mais próximos para uma avaliação médica!'
    )
    return probability
