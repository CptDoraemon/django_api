from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


class Post(models.Model):
    title = models.TextField(max_length=100, null=False, blank=False)
    content = models.TextField(max_length=5000, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


# @receiver(post_delete, sender=Post)
# def submission_delete(sender, instance):
#     instance.image.delete(False)


# def pre_save_post_receiver(sender, instance, *args, **kwargs):
#     if not instance.slug:
#         instance.slug = slugify(instance.owner.username + '-' + instance.title)
#
#
# pre_save.connect(pre_save_post_receiver, sender=Post)