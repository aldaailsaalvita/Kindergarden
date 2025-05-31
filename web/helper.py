import base64
import os
import subprocess
import uuid
# FOR COMPRESS IMAGE
from io import BytesIO

from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from PIL import Image as PILImage

APP_IMAGE_TYPES = ["image/jpeg", "image/gif", "image/png", "image/webp"]
APP_VIDEO_TYPES = ["video/mp4", "video/mpeg", "video/mov", "video/webm"]


def generate_video_thumbnail(file, image_path):
    s3_image_key = "media/" + image_path
    # video_path = 'https://s3-ap-southeast-1.amazonaws.com/lolab.staging/media/galleries/2021/8/6/7b83b3a9c0a84db4b876374e41350d17.mp4'
    video_path = file.url

    time = "00:00:00.000"

    # print(s3_image_key)
    # print(video_path)

    video = subprocess.run(
        ["ffmpeg", "-ss", time, "-i", video_path,
            "-f", "image2", "-vframes", "1", "-"],
        stdout=subprocess.PIPE,
    )

    contentType = "image/jpeg"
    # s3 = boto3.resource("s3")
    # s3.Object(settings.AWS_STORAGE_BUCKET_NAME,
    #           s3_image_key).put(Body=video.stdout, ACL='public-read', ContentType=contentType,)


# def get_mime_type(file):
#     """
#     Get MIME by reading the header of the file
#     """
#     initial_pos = file.tell()
#     file.seek(0)
#     mime_type = magic.from_buffer(file.read(1024), mime=True)
#     file.seek(initial_pos)
#     return mime_type


def compress_image(image):
    basewidth = 1920
    limit = 200000
    quality = 80
    # print(f"limit : {limit}")
    # print(f"file size : {len(image.file.read())}")

    # name = str(image).split('.')[0]
    img = PILImage.open(image)
    width, height = img.size
    # print(f"width x height original : {width} x {height}")

    while len(image.file.read()) > limit:
        basewidth -= 100
        # print(f"basewidth : {basewidth}")
        quality -= 10
        # print(f"quality: {quality}")

        width_percent = basewidth / float(img.size[0])
        height_size = int((float(img.size[1]) * float(width_percent)))

        # print(f"width x height compress : {basewidth} x {height_size}")
        # img = img.resize((basewidth, height_size), PILImage.ANTIALIAS)
        img = img.resize((basewidth, height_size), PILImage.LANCZOS)

    output = BytesIO()

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # save the resized file to our IO ouput with the correct format
    img.save(output, format="JPEG", quality=quality)

    newImage = File(output, name=image.name)
    return newImage


def compress_image_square(image):
    limit = 100000
    basewidth = 400
    quality = 80

    img = PILImage.open(image)

    # compress image
    while len(image.file.read()) > limit:
        # basewidth -= 100
        # print(f"basewidth : {basewidth}")
        # quality -= 10
        # print(f"quality: {quality}")

        width_percent = basewidth / float(img.size[0])
        height_size = int((float(img.size[1]) * float(width_percent)))

        # print(f"width x height compress : {basewidth} x {height_size}")
        # img = img.resize((basewidth, height_size), PILImage.ANTIALIAS)
        img = img.resize((basewidth, height_size), PILImage.LANCZOS)

    # When image height is greater than its width
    if img.height > img.width:
        # make square by cutting off equal amounts top and bottom
        left = 0
        right = img.width
        top = (img.height - img.width) / 2
        bottom = (img.height + img.width) / 2
        img = img.crop((left, top, right, bottom))
        # Resize the image to 300x300 resolution
        if img.height > basewidth or img.width > basewidth:
            output_size = (basewidth, basewidth)
            # img.thumbnail(output_size)
            # img.save(image)

    # When image width is greater than its height
    elif img.width > img.height:
        # make square by cutting off equal amounts left and right
        left = (img.width - img.height) / 2
        right = (img.width + img.height) / 2
        top = 0
        bottom = img.height
        img = img.crop((left, top, right, bottom))
        # Resize the image to 300x300 resolution
        if img.height > basewidth or img.width > basewidth:
            output_size = (basewidth, basewidth)
            # img.thumbnail(output_size)
            # img.save(image)

    output = BytesIO()

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # save the resized file to our IO ouput with the correct format
    img.save(output, format="JPEG", quality=quality)

    newImage = File(output, name=image.name)
    return newImage


@deconstructible
class RandomFileName(object):
    def __init__(self, path):
        now = timezone.now()
        re_path = "{}/{}/{}/{}/".format(path, now.year, now.month, now.day)
        self.path = os.path.join(re_path, "%s%s")

    def __call__(self, _, filename):
        # @note It's up to the validators to check if it's the correct file type in name or if one even exist.
        # print(filename)
        # print(self.path)
        file_name = os.path.splitext(filename)[0]
        file_extension = os.path.splitext(filename)[1]
        file_type = self.path.split("/")[0]
        # print(file_type)
        return self.path % (uuid.uuid4().hex, file_extension)


def normalize_image_url(img_url):
    other_url = "{}{}".format(settings.API["ENDPOINT"], img_url)
    url = img_url if img_url.startswith("http") else other_url
    return url


def base64_file(data, xname=None):
    # print(data)
    format, imgstr = data.split(';base64,')
    ext = format.split('/')[-1]
    image_file = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
    return image_file
