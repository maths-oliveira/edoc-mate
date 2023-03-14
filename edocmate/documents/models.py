from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Document(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')
    tags = models.ManyToManyField(Tag, related_name='documents')
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
