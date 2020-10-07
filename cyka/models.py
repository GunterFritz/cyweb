import uuid
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
    uuid = models.UUIDField( 
         primary_key = False, 
         default = uuid.uuid4, 
         editable = False) 

    def __str__(self):
        return self.name

class Member(models.Model):
    name = models.CharField(max_length=128)
    email = models.EmailField(max_length=254,blank=True, null= True, default="")
    uuid = models.UUIDField( 
         primary_key = False, 
         default = uuid.uuid4, 
         editable = False) 
    proj = models.ForeignKey(Project, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    mtype = models.CharField(max_length=16,choices=(('M', 'MEMBER'),('G', 'GUEST')),default='M')

#Statement of importance
class Card(models.Model):
    proj = models.ForeignKey(Project, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    heading = models.CharField(max_length=128)
    desc = models.TextField()

#Agreed Statement of importance
class Table(models.Model):
    #name = models.CharField(max_length=128)
    #desc = models.TextField()
    proj = models.ForeignKey(Project, on_delete=models.CASCADE)
    uuid = models.UUIDField( 
         primary_key = False, 
         default = uuid.uuid4, 
         editable = False)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, default=None)

#Likes for si
class CardVotes(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)

#Signs to si to make asi
class SIsign(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)

#Votes for topicauction
class AsiVotes(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)


class Topic(models.Model):
    name = models.CharField(max_length=128)
    number = models.IntegerField()
    desc = models.TextField()
    proj = models.ForeignKey(Project, on_delete=models.CASCADE)
    #list number in agenda(1 opposite of 2, 3 opposite of 4, ...)
    color = models.CharField(max_length=64, default="")
    agendanumber = models.IntegerField(null=True)
    #meeting can be started
    is_active = models.BooleanField(default=False)
    uuid = models.UUIDField( 
         primary_key = False, 
         default = uuid.uuid4, 
         editable = False) 
    asi = models.ForeignKey(Table, on_delete=models.CASCADE, default=None, blank=True, null=True)
    #asi = models.ForeignKey(Table, on_delete=models.CASCADE, default=None, blank=True, null=True)
    
    def __str__(self):
        return self.name

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

class WorkflowElement(models.Model):
    proj = models.ForeignKey(Project, on_delete=models.CASCADE)
    step = models.IntegerField(default=0)
    done = models.BooleanField(default=False)
    status = models.CharField(max_length=16,choices=(('O', 'OPEN'),('S', 'STARTED'), ('B', 'FINISHED')), default='O')

