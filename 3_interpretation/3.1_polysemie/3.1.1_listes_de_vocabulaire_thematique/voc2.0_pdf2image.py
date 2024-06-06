# Préparation pour l'OCR

from pdf2image import convert_from_path
import os

input = "/data/pdf"
output = "data/images"

for pdf in os.listdir(input):
    theme = pdf[:-4]
    output_dir = os.path.join(output, theme)
    os.makedirs(output_dir, exist_ok=True)
    images = convert_from_path(os.path.join(input,pdf))
    for i, image in enumerate(images):
        index = "{:02d}".format(i)
        output_img = os.path.join(output_dir,f'{theme}_{index}.png')
        image.save(output_img)