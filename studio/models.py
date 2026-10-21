from django.conf import settings
from django.db import models
class Project(models.Model):
 owner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='projects')
 title=models.CharField(max_length=120)
 description=models.TextField(blank=True,max_length=2000)
 created_at=models.DateTimeField(auto_now_add=True)
 updated_at=models.DateTimeField(auto_now=True)
 archived=models.BooleanField(default=False)
 def __str__(self):return self.title
class Asset(models.Model):
 project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='assets')
 kind=models.CharField(max_length=12,choices=[('reference','Reference'),('sketch','Sketch')])
 file_key=models.CharField(max_length=100,unique=True)
 created_at=models.DateTimeField(auto_now_add=True)
 source=models.ForeignKey('self',on_delete=models.SET_NULL,null=True,blank=True)
