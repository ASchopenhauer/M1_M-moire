# OCR : Français et Allemand

import pytesseract
import cv2
from ultralytics import YOLO
import os

model_path = "/data/best.pt"
mon_model = YOLO(model_path)
input = "/data/images_thèmes"
output = "/data/vocabulaire_fr_all"

for theme in os.listdir(input)[1:]:

    for name_img in os.listdir(os.path.join(input,theme))[2:]:
        output_tr = os.path.join(output,theme,name_img[:-4])
        os.makedirs(output_tr,exist_ok=True)

        path_img = os.path.join(input,theme,name_img)
        image = cv2.imread(path_img)
        result = mon_model.predict(path_img, save=True, boxes=True)
        boxes = result[0].boxes.data.cpu().numpy()

        i_fra = 0
        i_deu = 0

        for i, box in enumerate(boxes):

            x_min, y_min, x_max, y_max, confidence, class_id = box
            class_id = int(class_id)            

            if class_id == 0:

                region = image[int(y_min):int(y_max), int(x_min):int(x_max)]
                text = pytesseract.image_to_string(region, config='-l fra')
                open(os.path.join(output_tr,f"{theme}_p{name_img[-6:-4]}_{i_fra}_fra.txt"),'w').write(text)
                i_fra+=1

            if class_id == 1:

                region = image[int(y_min):int(y_max), int(x_min):int(x_max)]
                text = pytesseract.image_to_string(region, config='-l deu')
                open(os.path.join(output_tr,f"{theme}_p{name_img[-6:-4]}_{i_deu}_deu.txt"),'w').write(text)
                i_deu+=1
