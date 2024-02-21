from io import BytesIO
from matplotlib import pyplot as plt
from diffusers import StableDiffusionInpaintPipeline
from PIL import Image
import numpy as np
import cv2
import torch

# 원하는 GPU 번호 설정
gpu_number = 7
device = torch.device("cuda:" + str(gpu_number) if torch.cuda.is_available() else "cpu")


class Inpaint:
    def __init__(self, inpainting_prompt):
        self.inpainting_prompt = inpainting_prompt

    def inpaint_image(self):
        inpainting_prompt_values = " ".join(self.inpainting_prompt)
        print(inpainting_prompt_values)

        # jpg로 수정
        img2 = Image.open("/home/zio/rasa1/rasa/diffuser/snowman_hat_mask.png")
        width, height = img2.size
        # 새로운 이미지 생성
        new_image = Image.new("RGB", (width, height), color=(0, 0, 0))  # 검정색 배경

        # 특정 색상 보존 (민트색)
        preserved_color = (0, 255, 255)
        white = (255, 255, 255)
        tolerance = 50  # 허용 오차

        # 이미지 픽셀 순회
        for x in range(width):
            for y in range(height):
                pixel = img2.getpixel((x, y))
                distance = sum((a - b) ** 2 for a, b in zip(pixel, preserved_color)) ** 0.5
                if distance < tolerance:
                    new_image.putpixel((x, y), white)
        # 마스크 분리해서 저장
        new_image.save('/home/zio/rasa1/rasa/diffuser/mask.png')

        # 솔리드화
        mask_image = (Image.open("/home/zio/rasa1/rasa/diffuser/mask.png").convert("L")).resize((512, 512))
        binary_mask = np.array(mask_image)
        threshold_value = 127  
        binary_mask[binary_mask <= threshold_value] = 0
        binary_mask[binary_mask > threshold_value] = 255
        binary_mask = np.uint8(binary_mask) 
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
        largest_contour = max(contours, key=cv2.contourArea) 
        approx_points = cv2.approxPolyDP(largest_contour, 0.02 * cv2.arcLength(largest_contour, True), True) 
        output_image = cv2.cvtColor(binary_mask, cv2.COLOR_GRAY2BGR) 
        cv2.polylines(output_image, [approx_points], isClosed=True, color=(255, 0, 0), thickness=2) 
        cv2.fillPoly(output_image, [approx_points], (255, 0, 0))
        output_image[(output_image == [255, 255, 255]).all(axis=2)] = [0, 0, 0]  
        output_image[(output_image == [255, 0, 0]).all(axis=2)] = [255, 255, 255]  
        cv2.imwrite("/home/zio/rasa1/rasa/diffuser/mask.png", output_image) # solidify된 흑백 마스킹 이미지 저장 
        

        init_image = Image.open('/home/zio/rasa1/rasa/diffuser/snowman_zio.png')
        init_image =  init_image.convert("RGB").resize((512, 512))
        # image = image.resize((512, 512))

        mask = Image.open('/home/zio/rasa1/rasa/diffuser/mask.png')
        mask = mask.convert("RGB").resize((512, 512))
        # mask.save('cat_mask.PNG')

        pipe = StableDiffusionInpaintPipeline.from_pretrained(
            "runwayml/stable-diffusion-inpainting", torch_dtype=torch.float16
        )
        pipe = pipe.to(f"cuda:{gpu_number}")

        # prompt=
        image = pipe(inpainting_prompt_values, image=init_image, mask_image=mask).images[0]
        image = image.resize((700,700))
        image.save('/home/zio/rasa1/rasa/diffuser/inpainted.png')



        print("---------- inpainting_prompt testing----------")
        print(inpainting_prompt_values)


current_inpainting_prompt_value = "a snowman with a hat."
diffusion = Inpaint(current_inpainting_prompt_value)
diffusion.inpaint_image()