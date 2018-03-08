from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Project(models.Model):
	name = models.CharField(max_length=64)
	question = models.TextField()
	admin = models.ForeignKey(User, on_delete=models.CASCADE)
	ptype = models.CharField(max_length=32,choices=(('I', 'IKOSAEDER'),('O', 'OKTAEDER')))
	#don't recalculate agenda if already exists
	hasagenda = models.BooleanField(default=False)

	def __str__(self):
		return self.name

class Topic(models.Model):
	name = models.CharField(max_length=128)
	number = models.IntegerField()
	desc = models.TextField()
	proj = models.ForeignKey(Project, on_delete=models.CASCADE)
	#list number in agenda(1 opposite of 2, 3 opposite of 4, ...)
	color = models.CharField(max_length=64, default="")
	agendanumber = models.IntegerField()
	
	def __str__(self):
		return self.name

class Member(models.Model):
	name = models.CharField(max_length=128)
	proj = models.ForeignKey(Project, on_delete=models.CASCADE)
	status = models.BooleanField(default=False)

"""
M:N for the priorization of topic
"""
class Priority(models.Model):
	priority = models.IntegerField(default=20)
	topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
	member = models.ForeignKey(Member, on_delete=models.CASCADE)

"""
M:N Assignment from Member to Topic
"""
class Assignment(models.Model):
	atype = models.CharField(max_length=16,choices=(('M', 'MEMBER'),('C', 'CRITIC')))
	topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
	member = models.ForeignKey(Member, on_delete=models.CASCADE)
