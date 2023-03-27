from django.db import models

class Person(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.name}"


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.name}"


class TType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.name}"


class Other(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.name}"

class Document(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')

    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    ttype = models.ForeignKey(TType, on_delete=models.SET_NULL, null=True, blank=True)
    other = models.ForeignKey(Other, on_delete=models.SET_NULL, null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Dossier(models.Model):
    name = models.CharField(max_length=100)
    documents = models.ManyToManyField(Document, related_name='dossiers')

    def __str__(self):
        return f"{self.name}"
