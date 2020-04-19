from storages.backends.s3boto3 import S3Boto3Storage
import os
from urllib.parse import urlparse
import time
from numpy import base_repr
from account.utils.resize_image import resize_image


def validate_and_save_image(file, post_id, file_index):
    # resize, optimize and check size
    # file = resize_image(file, file.name, 200, 200)
    # if file.size > 5 * 1024 * 1024:

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