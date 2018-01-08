from lib.algorithm import Structure
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth import authenticate, login
from .forms import ProjectForm, TopicForm, MemberForm
from .models import Project, Topic, Member
# Create your views here.

def project(request):
	username = None
	if request.user.is_authenticated():
		username = request.user.username
	else:
		return HttpResponse("Permission denied")

	#projects = Project.objects.get()
	#projects = request.user.

	return HttpResponse(username)
	
def project_details(request, project_id):
	try:
		project = Project.objects.get(pk=project_id)
	except Project.DoesNotExist:
		raise Http404("Project does not exist")
	return render(request, 'cyka/project_details.html', {'project' : project })
	#projects = Project.objects.all()

def member_new(request, project_id):
	try:
		project = Project.objects.get(pk=project_id)
	except Project.DoesNotExist:
		raise Http404("Project does not exist")
	
	if request.method == 'POST':
		form = MemberForm(request.POST)
		if form.is_valid():
			member = form.save(commit=False)
			member.proj = project
			member.save()
		return redirect('cyka:project_team', project_id)
	else:
		form = MemberForm()
	return render(request, 'cyka/member_add.html', {'project' : project, 'form' : form })

def member_edit_up(request, member_id, priority):
	try:
		member = Member.objects.get(pk=member_id)
		priority_list = member.priority_set.all()

		if len(priority_list) == 0:
			priority_list = create_priority_list(member)
	except Member.DoesNotExist:
		raise Http404("Member does not exist")

	priority = int(priority)
	#arrow up: switch to elements
	for p in priority_list:
		if p.priority == priority - 1:
			p.priority = priority
			p.save()
		elif p.priority == priority:
			p.priority = priority - 1
			if p.priority < 0:
				p.priority = 0
			p.save()

	return redirect('cyka:member_edit', member_id)

def member_edit(request, member_id):
	try:
		member = Member.objects.get(pk=member_id)
		priority_list = member.priority_set.all().order_by('priority')

		if len(priority_list) == 0:
			priority_list = create_priority_list(member)

	except Member.DoesNotExist:
		raise Http404("Member does not exist")
	return render(request, 'cyka/member_edit.html', {'project' : member.proj, 'member': member, 'priority_list':priority_list })

def project_team(request, project_id):
	try:
		project = Project.objects.get(pk=project_id)
	except Project.DoesNotExist:
		raise Http404("Project does not exist")
	return render(request, 'cyka/project_team.html', {'project' : project })
	
def project_topics(request, project_id):
	try:
		project = Project.objects.get(pk=project_id)
		topics = project.topic_set.all()
		if len(topics) == 0:
			topics = create_topics(project)
	except Project.DoesNotExist:
		raise Http404("Project does not exist")
	return render(request, 'cyka/project_topics.html', {'project' : project })
	
def project_list(request):
	projects = Project.objects.all()
	return render(request, 'cyka/project_list.html', {'projects': projects})

def topic_edit(request, topic_id):
	try:
		topic = Topic.objects.get(pk=topic_id)
	except Topic.DoesNotExist:
		raise Http404("Topic does not exist")

	if request.method == 'POST':
		form = TopicForm(request.POST, instance=topic)
		topic = form.save(commit=False)
		topic.save()
		return render(request, 'cyka/project_topics.html', {'project': topic.proj})
	else:
		form = TopicForm(instance=topic)
	return render(request, 'cyka/topic_edit.html', {'project': topic.proj, 'form': form, 'topic': topic})

def project_new(request):
	if request.method == 'POST':
		form = ProjectForm(request.POST)
		if form.is_valid():
			prj = form.save(commit=False)
			prj.admin = request.user
			prj.save()
			create_topics(prj)
		#return redirect('cyka:project_list', pk=post.pk)
		return redirect('cyka:project_list')
	else:
		form = ProjectForm()
	return render(request, 'cyka/project_edit.html', {'form': form})


def login(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(request, username=username, password=password)
	
	if user is not None:
		# Redirect to a success page.
		login(request, user)
		return HttpResponseRedirect(reverse('cyka:project'))
	else:
        	# Return an 'invalid login' error message.
		return HttpResponse("login failed")

def create_topics(prj):
	num = Structure.factory(prj.ptype).getNumTopics()
	for i in range(1, num +1):
		prj.topic_set.create(number=i)
	
	return prj.topic_set.all()

def create_priority_list(person):
	topics =  person.proj.topic_set.all()
	if len(topics) == 0:
		return None
	i=0
	for t in topics:
		person.priority_set.create(priority=i, topic=t)
		i=i+1

	return person.priority_set.all()
