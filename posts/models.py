from django.db import models


class Post(models.Model):
    title = models.TextField()
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    # owner = models.ForeignKey('User', on_delete=models.SET_NULL)

    class Meta:
        ordering = ['created']
