from django.apps import AppConfig


class StartUpConfig(AppConfig):
    name = 'start_up'

    def ready(self):
        # do a query to database to accelerate first connection after app starts
        from posts.models import Post
        print(f'App ready: {Post.objects.all().count()} posts in total.')
