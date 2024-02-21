# draw.py 수정본
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
from controlnet_aux import HEDdetector
import torch
import requests
from PIL import Image
from io import BytesIO
#from rembg import remove
class Draw:
    def __init__(self, drawing_object, drawing_prompt):
        self.drawing_object = drawing_object
        self.drawing_prompt = drawing_prompt
        
    def draw_image(self):
        
        drawing_object_values = "".join(self.drawing_object)
        drawing_prompt_values = ", ".join(self.drawing_prompt)

        image = Image.open('/home/public/zio/mmchatbot/file_receive.jpg') # Change to your path
        model_path = "runwayml/stable-diffusion-v1-5"
        # 사진 윤곽선 따기
        hed = HEDdetector.from_pretrained("lllyasviel/Annotators")
        # image = image.resize((456, 600))
        image = image.resize((512, 512))
        image = hed(image)
        # controlnet
        controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/sd-controlnet-scribble", torch_dtype=torch.float16
        )
        pipe = StableDiffusionControlNetPipeline.from_pretrained(
        model_path, controlnet=controlnet, safety_checker=None, torch_dtype=torch.float16
        )
        pipe = pipe.to("cuda")
        # 스케듈러
        pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
        # lms = LMSDiscreteScheduler.from_config(pipe.scheduler.config)
        # pipe.scheduler = lms
        # 스케듈러 뭘로 할지 확인 필요
        pipe.enable_model_cpu_offload()
        # generator = torch.manual_seed(1)
        image = pipe(drawing_prompt_values, image, num_inference_steps=10).images[0]
        image = image.resize((700,700))
        # 배경 제거하기
        #out = remove(image)
        image.save('/home/public/zio/mmchatbot/static/js/change.png')  # Change to your path
        print("---------- draw.py drawing_object ----------")
        print(drawing_object_values)
        print("---------- draw.py drawing_prompt ----------")
        print(drawing_prompt_values)