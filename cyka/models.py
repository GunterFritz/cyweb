from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Project(models.Model):
	name = models.CharField(max_length=64)
	question = models.TextField()
	admin = models.ForeignKey(User, on_delete=models.CASCADE)
	ptype = models.CharField(max_length=32,choices=(('I', 'IKOSAEDER'),('O', 'OKTAEDER')))

	def __str__(self):
		return self.name

class Topic(models.Model):
	name = models.CharField(max_length=128)
	number = models.IntegerField()
	desc = models.TextField()
	proj = models.ForeignKey(Project, on_delete=models.CASCADE)
	
	def __str__(self):
		return self.name

class Member(models.Model):
	name = models.CharField(max_length=128)
	proj = models.ForeignKey(Project, on_delete=models.CASCADE)

class Priority(models.Model):
	priority = models.IntegerField(default=20)
	topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
	member = models.ForeignKey(Member, on_delete=models.CASCADE)
