import rembg
from PIL import Image
img = Image.open("/home/zio/rasa1/Lenna.png")
out = rembg.remove(img)
out.save("Lenna_removebg.png")