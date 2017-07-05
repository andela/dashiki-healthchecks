from django.db import models
from ckeditor.fields import RichTextField


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
