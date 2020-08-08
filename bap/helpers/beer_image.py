import requests
import numpy as np
import cv2

from PIL import Image
from io import BytesIO


def load_img_from_url(url: str):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))


def resize_image(img_, scale_percent: int = 60):
    width = int(img_.shape[1] * scale_percent / 100)
    height = int(img_.shape[0] * scale_percent / 100)
    dim = (width, height)
    # resize image
    return cv2.resize(img_, dim, interpolation = cv2.INTER_AREA)


def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


def remove_background(img):
    mask = np.zeros(img.shape[:2], np.uint8)
    background_model = np.zeros((1, 65), np.float64)
    foreground_model = np.zeros((1, 65), np.float64)

    rectangle = (0, 0, 600, 900)
    cv2.grabCut(img, mask, rectangle, background_model, foreground_model, 5,
                cv2.GC_INIT_WITH_RECT)

    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    img = img * mask2[:, :, np.newaxis]
    r_img = rotate_image(img, 15)

    _, thresh = cv2.threshold(cv2.cvtColor(r_img, cv2.COLOR_BGR2GRAY), 0, 35, cv2.THRESH_BINARY)
    r_img[thresh == 0] = (255, 255, 255)
    return img


def add_beer_background(img):
    background = cv2.resize(
        cv2.imread("images/background5.jpg"),
        (819, 819),
        interpolation=cv2.INTER_AREA
    )
    added_image = cv2.addWeighted(cv2.cvtColor(background, cv2.COLOR_BGR2RGB), 0.4, img, 0.7, -50)
    return added_image
