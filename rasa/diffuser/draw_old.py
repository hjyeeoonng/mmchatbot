# Drawing
# from PIL import Image
# from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
# import torch
# from controlnet_aux import HEDdetector
# from diffusers.utils import load_image

import torch
import requests
from PIL import Image
from io import BytesIO
from diffusers import StableDiffusionImg2ImgPipeline



class Draw:
    def __init__(self, drawing_object, drawing_prompt):
        self.drawing_object = drawing_object
        self.drawing_prompt = drawing_prompt

    def draw_image(self):

        drawing_object_values = "".join(self.drawing_object)
        drawing_prompt_values = "".join(self.drawing_prompt)

        image = Image.open('/home/zio/rasa1/file_receive.jpg')
        image = image.resize((456, 600))
        
        device = "cuda"
        #"runwayml/stable-diffusion-v1-5"
        #"/home/irteam/su1433-dcloud-dir/suhan/finetuned-model"
        model_path = "/home/irteam/su1433-dcloud-dir/suhan/finetuned-model"
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            model_path, revision="fp16", torch_dtype=torch.float16
        ).to(device)
       
        pipe = pipe.to(device)

        # pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
# 
        pipe.enable_model_cpu_offload()

        # generator = torch.manual_seed(1)
        image = pipe(drawing_prompt_values, image, num_inference_steps=10).images[0]
        image = image.resize((700,700))
        image.save('/home/zio/rasa1/static/js/change.png')
        

        print("---------- drawing_object ----------")
        print(drawing_object_values)
        print("---------- drawing_prompt ----------")
        print(drawing_prompt_values)



