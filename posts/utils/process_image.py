from storages.backends.s3boto3 import S3Boto3Storage
import os
import time
from numpy import base_repr
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from rest_framework import serializers


def validate_and_and_optimize_images(files):
    processed_images = []

    for i, file_string in enumerate(files):
        file = files[file_string]
        _validate_image(file)

    for i, file_string in enumerate(files):
        file = files[file_string]
        processed_images.append(_optimize_images(file))

    return processed_images


def _optimize_images(file):
    image = Image.open(file)
    image.thumbnail((2000, 2000), Image.ANTIALIAS)
    buffer = BytesIO()
    image.save(fp=buffer, format='JPEG', quality=85, optimize=True)
    return ContentFile(buffer.getvalue(), name=file.name)


def _validate_image(file):
    try:
        # load() is the only method that can spot a truncated JPEG,
        #  but it cannot be called sanely after verify()
        trial_image = Image.open(file)
        trial_image.load()

        # Since we're about to use the file again we have to reset the
        # file object if possible.
        if hasattr(file, 'reset'):
            file.reset()

        # verify() is the only method that can spot a corrupt PNG,
        #  but it must be called immediately after the constructor
        trial_image = Image.open(file)
        trial_image.verify()

    except Exception:  # Python Imaging Library doesn't recognize it as an image
        raise serializers.ValidationError({'image': 'image error'})


def save_image(file, post_id, file_index):
    # vars
    file_directory_within_bucket = 'post_images/{0}/'.format(post_id)
    media_storage = S3Boto3Storage()

    # save image
    random_string = base_repr(int(time.time() * 1000), 36)
    file_name = '{0}_{1}{2}'.format(file_index, random_string, os.path.splitext(file.name)[1])
    file_path_within_bucket = os.path.join(
        file_directory_within_bucket,
        file_name
    )
    media_storage.save(file_path_within_bucket, file)

    return media_storage.url(file_path_within_bucket)


def delete_image_folder(post_id):
    # vars
    directory = 'post_images/{0}/'.format(post_id)
    media_storage = S3Boto3Storage()

    # delete
    media_storage.bucket.objects.filter(Prefix=directory).delete()
