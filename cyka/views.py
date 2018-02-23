from lib.algorithm import Structure
from lib.algorithm import Topic as A_Topic
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth import authenticate, login
from .forms import ProjectForm, TopicForm, MemberForm, MemberOkForm
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

"""
is called when priority of a topic is changed in member_edit
it resorts the list

params
-------
member_id: private key
priority: position of topic that was clicked
"""
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

def member_ok(request, member_id, ok):
	try:
		member = Member.objects.get(pk=member_id)
	except Member.DoesNotExist:
		raise Http404("Member does not exist")
	member.status = ok
	member.save()
	return redirect('cyka:member_edit', member_id)

"""
edit view of member
"""
def member_edit(request, member_id):
	try:
		member = Member.objects.get(pk=member_id)
		priority_list = member.priority_set.all().order_by('priority')

		if len(priority_list) == 0:
			priority_list = create_priority_list(member)

	except Member.DoesNotExist:
		raise Http404("Member does not exist")
	
	if request.method == 'POST':
		form = MemberOkForm(request.POST)
		if form.is_valid():
			form = MemberOkForm(request.POST, instance=member)
			member = form.save(commit=False)
			member.save()
	else:
		form = MemberOkForm(instance=member)
	return render(request, 'cyka/member_edit.html', {'project' : member.proj, 'member': member, 'priority_list':priority_list, 'form' : form })

def agenda(request, project_id):
	try:
		project = Project.objects.get(pk=project_id)
	except Project.DoesNotExist:
		raise Http404("Project does not exist")
	members = project.member_set.all()
	struct = Structure.factory(project.ptype)
	if len(members)< struct.getMinPersons():
		err_text = "Minimale Anzahl Teilnhemer nicht erreicht"
	arr = []
	err_text = ""
	for m in members:
		if m.status == False:
			err_text = "Teilnhemer müsser ihre Themenliste bestätigen"
			#break;
		else:
			arr.append(get_priority_list(m))
	arr = get_count_stat(project)
	if err_text != "":
		#do not create agenda
		return render(request, 'cyka/project_agenda_err.html', {'project' : project, 'err_text' : err_text, 'arr' : arr})
	#create agenda
	agenda = get_agenda(project)
	return render(request, 'cyka/project_agenda.html', {'project' : project, 'agenda' : agenda })



def project_team(request, project_id):
	try:
		project = Project.objects.get(pk=project_id)
	except Project.DoesNotExist:
		raise Http404("Project does not exist")
	struct = Structure.factory(project.ptype)
	return render(request, 'cyka/project_team.html', {'project' : project, 'min' : struct.getMinPersons(), 'max' : struct.getMaxPersons() })
	
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
	if not request.user.is_authenticated():
		return redirect('/admin')
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

"""
helper function create topics for project and add it to database

params
-------
prj:	database object Project

return
-------
list of topics
"""
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

#returns the priority for a person as list
def get_priority_list(person):
	plist = person.priority_set.all().order_by('priority')
	retval = [person.id]
	for p in plist:
		retval.append(p.topic.number)
	return retval

#creates an array that can be used as input for structure object
def create_if_list(proj):
	retval = []
	for p in proj.member_set.all():
		retval.append(get_priority_list(p))
	print("---")
	print(retval)
	print("---")
	return retval

#statistical information, returns for each topic how many people vote for it
def get_count_stat(proj):
	struct = Structure.factory(proj.ptype)
	struct.array_init(create_if_list(proj))
	arr = struct.count_popularity()
	print(arr)
	return arr

def switch(proj, t):
	topics =  proj.topic_set.all()
	for db in topics:
		if db.number == t.index:
			return db
	return None

def get_agenda(proj):
	struct = Structure.factory(proj.ptype)
	struct.array_init(create_if_list(proj))
	agenda = struct.getAgenda()
	dbagenda = []
	for t in agenda:
		print(t)
		dbagenda.append([switch(proj, t[0]), switch(proj, t[1])])
	#print(agenda)
	return dbagenda
