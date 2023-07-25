#Sometimes NASA API will return an image that is not supported by instagram aspect ratio. 
#So we will use Pillow to resize the image to a supported aspect ratio by putting black bars on the sides.
from PIL import Image
import requests
from io import BytesIO



'''
for VSCode testing

import matplotlib.pyplot as plt
import numpy as np


def format_image(image_url):
    # Use requests to download the image from the URL
    response = requests.get(image_url)

    # Use BytesIO to create a file-like object from the response content
    image_data = BytesIO(response.content)

    # Use Image.open to open the image from the file-like object
    image = Image.open(image_data)

    org_width, org_height = image.size

    aspect_ratio = org_width / org_height

    if org_width > org_height:
        new_width = 1080
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = 1080
        new_width = int(new_height * aspect_ratio)

    resized_image = image.resize((new_width, new_height))

    final_image = Image.new("RGB", (1080, 1080), (0, 0, 0))
    x_offset = int((1080 - new_width) // 2)
    y_offset = int((1080 - new_height) // 2)
    final_image.paste(resized_image, (x_offset, y_offset))

    # Convert the final_image to bytes
    buffer = BytesIO()
    final_image.save(buffer, format="JPEG")
    buffer.seek(0)

    return np.array(final_image)
'''
def format_image(image_url):
    # Use requests to download the image from the URL
    response = requests.get(image_url)

    # Use BytesIO to create a file-like object from the response content
    image_data = BytesIO(response.content)

    # Use Image.open to open the image from the file-like object
    image = Image.open(image_data)

    org_width, org_height = image.size

    aspect_ratio = org_width / org_height

    if org_width > org_height:
        new_width = 1080
        new_height = int(new_width / aspect_ratio)
    else:
        new_height = 1080
        new_width = int(new_height * aspect_ratio)

    resized_image = image.resize((new_width, new_height))

    final_image = Image.new("RGB", (1080, 1080), (0, 0, 0))
    x_offset = int((1080 - new_width) // 2)
    y_offset = int((1080 - new_height) // 2)
    final_image.paste(resized_image, (x_offset, y_offset))

    # Convert the final_image to bytes (no longer using numpy or matplotlib)
    buffer = BytesIO()
    final_image.save(buffer, format="JPEG")
    buffer.seek(0)

    return buffer


image = format_image("https://apod.nasa.gov/apod/image/2307/MWAurora_hang_960.jpg")

'''# show the image
plt.imshow(image)
plt.show()'''