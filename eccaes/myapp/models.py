from django.db import models
from django.utils import timezone

class userreg(models.Model):
    name = models.CharField(max_length=100) #
    email = models.CharField(max_length=50) #
    password = models.CharField(max_length=100) #
    contact = models.CharField(max_length=100) #
    address = models.CharField(max_length=200) #
    status = models.CharField(max_length=100, default='Deactivated') #
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "userreg" #

class Encryptedmodel(models.Model):
    useremail = models.CharField(null=True, max_length=100) #
    textcontent = models.CharField(null=True, max_length=100) #
    filekey = models.CharField(null=True, max_length=100) #
    datetime = models.DateTimeField(null=True, default=timezone.now) #
    encfilepath = models.CharField(null=True, max_length=100) #
    decfilepath = models.CharField(null=True, max_length=100) #
    filename = models.CharField(null=True, max_length=100) # Original filename
    filetype = models.CharField(null=True, max_length=50) # File type (text/file)

    class Meta:
        db_table="encryptmodel" #

class Filerequestmodel(models.Model):
    fileid = models.CharField(null=True, max_length=100) #
    useremail = models.EmailField(null=True) #
    textcontent = models.CharField(null=True, max_length=100) #
    receiveremail = models.CharField(null=True, max_length=100) #
    filekey = models.CharField(null=True, max_length=100) #
    datetime = models.DateTimeField(null=True, default=timezone.now) #
    status = models.CharField(default='pending', max_length=100) #

    class Meta:
        db_table= "filerequest" #
