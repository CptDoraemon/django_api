from django.db import models
from django.conf import settings
from posts.models import Post
from comments.models import Comment


class UserActions(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)

    liked_posts = models.ManyToManyField(Post, related_name='liked_by')
    disliked_posts = models.ManyToManyField(Post, related_name='disliked_by')
    liked_comments = models.ManyToManyField(Comment, related_name='liked_by')
    disliked_comments = models.ManyToManyField(Comment, related_name='disliked_by')

    saved_posts = models.ManyToManyField(Post, related_name='saved_by')
    saved_comments = models.ManyToManyField(Comment, related_name='saved_by')

    # def __str__(self):
    #     return self.u