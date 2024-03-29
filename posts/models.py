from email.policy import default
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone

TAG_CHOICES = [
    ('MISC', 'Miscellaneous'),
    ('WEB DEVELOPMENT', 'Web Development'),
    ('PHOTO', 'Photo'),
    ('NEWS', 'News'),
    ('GAME', 'Game'),
    ('TEST', 'Test'),
]
TAGS = list(map(lambda pair: pair[0], TAG_CHOICES))


class Post(models.Model):

    title = models.TextField(max_length=200, null=False, blank=False)
    content = models.TextField(max_length=200000, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    tag = models.CharField(max_length=20,
                           choices=TAG_CHOICES,
                           default=TAG_CHOICES[0][0])
    view_count = models.IntegerField(default=0)
    is_pinned = models.BooleanField(default=False)
    pinned_date = models.DateTimeField(default=timezone.now)

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
