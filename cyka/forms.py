from django import forms
from django.forms import ModelForm
from .models import Project, Topic, Member

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'question', 'ptype')


class TopicForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['desc'].required = False
        
    class Meta:
        model = Topic
        fields = ('name', 'desc',)

class MemberForm(ModelForm):
    class Meta:
        model = Member
        fields = ('name', 'email')

class MemberOkForm(ModelForm):
    class Meta:
        model = Member
        fields = ('status',)
