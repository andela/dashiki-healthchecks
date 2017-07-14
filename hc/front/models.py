from django.contrib.auth.models import User
from django.db import models

from hc.front.time_stamped_model import TimeStampedModel


class Post(TimeStampedModel):
    user = models.ForeignKey(User, blank=True, null=False, related_name="posts")
    title = models.CharField(max_length=256, null=False)
    body = models.TextField(null=True)
    slug = models.CharField(max_length=400, null=False, unique=True)
    publish = models.BooleanField(default=False)

    def save(self, **kwargs):
        self.slug = self._generate_slug(self.title)
        return super(Post, self).save(**kwargs)

    def _generate_slug(self, title):
        slug = "-".join([str(token) for token in title.lower().split(" ")])
        if Post.objects.filter(slug=slug).all():
            slug = slug + "-" + str(Post.objects.last().id + 1)
        return slug

