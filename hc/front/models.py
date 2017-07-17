from tinymce.models import HTMLField

from django.contrib.auth.models import User
from django.db import models
from ckeditor.fields import RichTextField

from hc.front.time_stamped_model import TimeStampedModel


class Post(TimeStampedModel):
    user = models.ForeignKey(User, blank=True, null=False, related_name="posts")
    title = models.CharField(max_length=256, null=False)
    body = HTMLField()
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


# Create your models here.
class FaqCategory(models.Model):
    category = models.CharField(max_length=100, blank=False, unique=True)

    def __str__(self):
        return "{}".format(self.category)


class FaqItem(models.Model):
    title = models.CharField(max_length=100, blank=False)
    body = RichTextField(max_length=2000, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(FaqCategory, on_delete=models.CASCADE)

    def __str__(self):  # pragma: no cover
        return "{} -> {}".format(self.category, self.title)
