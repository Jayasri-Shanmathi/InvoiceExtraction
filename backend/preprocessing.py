import cv2
import numpy as np
from PIL import Image

MAX_WIDTH = 1024
MAX_HEIGHT = 1024

def preprocess_image(pil_image: Image.Image) -> Image.Image:
    img = np.array(pil_image) 
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    h, w = img.shape[:2]
    scale = min(MAX_WIDTH / w, MAX_HEIGHT / h, 1.0)

    if scale < 1.0:
        img = cv2.resize(
            img,
            (int(w * scale), int(h * scale)),
            interpolation=cv2.INTER_AREA
        )

    img = cv2.GaussianBlur(img, (3, 3), 0)
    return Image.fromarray(img)
