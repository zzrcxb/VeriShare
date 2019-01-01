from django.db import models


class UserFile(models.Model):
    filename = models.CharField(max_length=255)
    alias = models.CharField(max_length=32, default=None)
    passwd = models.CharField(max_length=6)
    uploaded_date = models.DateTimeField('Upload Datetime')
    life = models.IntegerField(default=0)
    sha1 = models.CharField(max_length=40)
    public = models.BooleanField(default=False)
