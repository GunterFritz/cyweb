from django.forms import ModelForm
from .models import Project, Topic, Member

class ProjectForm(ModelForm):
	class Meta:
		model = Project
		fields = ('name', 'question', 'ptype')

class TopicForm(ModelForm):
	class Meta:
		model = Topic
		fields = ('name', 'desc',)

class MemberForm(ModelForm):
	class Meta:
		model = Member
		fields = ('name',)

class MemberOkForm(ModelForm):
	class Meta:
		model = Member
		fields = ('status',)
