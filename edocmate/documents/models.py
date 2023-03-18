from django.db import models


class Document(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')
    labels = models.ManyToManyField('Label', through='DocumentLabel')
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Label(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.name}"

class DocumentLabel(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.label} - {self.value}"


class Dossier(models.Model):
    name = models.CharField(max_length=100)
    documents = models.ManyToManyField(Document, related_name='dossiers')
    def __str__(self):
        return f"{self.name}"