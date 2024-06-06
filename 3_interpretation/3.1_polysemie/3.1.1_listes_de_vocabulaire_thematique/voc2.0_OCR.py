# OCR

import os
import pytesseract
import cv2
from ultralytics import YOLO

input = "/data/images"
output = "/output"

model_path = "/data/best.pt"
mon_model = YOLO(model_path)

for theme in os.listdir(input):

    texts = ""
    
    for img in os.listdir(os.path.join(input,theme)):
        path_image = os.path.join(input,theme,img)

        image = cv2.imread(path_image)
        result = mon_model.predict(path_image, save=True, boxes=True)
        boxes = result[0].boxes.data.cpu().numpy()
        class_id = result[0].boxes.cls.cpu().numpy()
        for i, box in enumerate(boxes):
            x_min, y_min, x_max, y_max, confidence, class_id = box
            class_id = int(class_id)
            if class_id == 1:
                region = image[int(y_min):int(y_max), int(x_min):int(x_max)]
                text = pytesseract.image_to_string(region, config='-l deu') + "\n"
                texts += text
        
    # sauvegarder dans un fichier texte
    open(os.path.join(output,f"{theme}.txt"), mode='w', encoding='utf-8').write(texts)