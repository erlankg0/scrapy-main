import numpy as np
from PIL import Image

# загрузка изображения
image = Image.open("KIA/Kia_Rio/rio_0.jpg")

# конвертирование изображения в массив numpy
img_array = np.array(image)

# получение размеров изображения
height, width, depth = img_array.shape

# поменять местами до 10 пикселей в случайном порядке
for i in range(10):
    x1 = np.random.randint(0, width)
    y1 = np.random.randint(0, height)
    x2 = np.random.randint(0, width)
    y2 = np.random.randint(0, height)
    img_array[y1, x1], img_array[y2, x2] = img_array[y2, x2], img_array[y1, x1]

# сохранение уника лизированного изображения
new_image = Image.fromarray(img_array.astype('uint8'))
new_image.save("unique_image.jpg")
