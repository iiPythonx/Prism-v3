# Copyright 2021 iiPython

# Modules
import io
import requests
from PIL import Image

# Image class
class Images(object):
    def compile(self, data: bytes) -> io.BytesIO:
        arr = io.BytesIO()
        data.save(arr, format = "PNG")
        arr.seek(0)
        return arr

    def imagefromURL(self, url: str) -> Image:
        try:
            return Image.open(io.BytesIO(requests.get(url, timeout = 2).content))

        except Exception:
            return None

    def compileGIF(self, images, duration) -> io.BytesIO:
        arr = io.BytesIO()
        images[0].save(arr, "GIF", save_all = True, append_images = images[1:], optimize = False, duration = duration, loop = 0)
        arr.seek(0)
        return arr
