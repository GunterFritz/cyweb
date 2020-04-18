from lib.structure import Structure2 as Structure
from lib.structure import Topic as A_Topic
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm, TopicForm, MemberForm, MemberOkForm
from .models import Project, Topic, Member, Assignment
from random import randrange 
from . import helpers
from .helpers import Agenda

# Create your views here.

@login_required
def project(request):
    username = None
    if request.user.is_authenticated():
        username = request.user.username
    else:
        return HttpResponse("Permission denied")

    #projects = Project.objects.get()
    #projects = request.user.

    return HttpResponse(username)
    
@login_required
def project_details(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    return render(request, 'cyka/project_details.html', {'project' : project })
    #projects = Project.objects.all()

@login_required
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
@login_required
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
"""
function to resort the topics random
is used for test puprose

params
-------
member_id: private key of member
"""
@login_required
def member_shuffle_topics(request, member_id):
    try:
        member = Member.objects.get(pk=member_id)
        priority_list = member.priority_set.all()

        if len(priority_list) == 0:
            priority_list = create_priority_list(member)
    except Member.DoesNotExist:
        raise Http404("Member does not exist")
    print("shuffle", member_id)

    #shuffle
    for p in priority_list:
        p1 = randrange(priority_list.count())
        p2 = p.priority
        
        #switch to priorities
        p.priority = priority_list[p1].priority
        p.save()
        priority_list[p1].priority = p2
        priority_list[p1].save()
      
    return redirect('cyka:member_edit', member_id)


	
def member_ok(request, member_id, ok):
    try:
        member = Member.objects.get(pk=member_id)
    except Member.DoesNotExist:
        raise Http404("Member does not exist")
    member.status = ok
    member.save()
    return redirect('cyka:member_edit', member_id)

@login_required
def project_delete(request, project_id):
    try:
        proj = Project.objects.get(pk=project_id)

        if (proj.admin != request.user):
            return HttpResponseForbidden('Access Denied')
        helpers.ProjectDelete(proj)
        
        return redirect('cyka:project_list')

    except Member.DoesNotExist:
        raise Http404("Project delete error")

@login_required
def member_delete(request, member_id):
    try:
        member = Member.objects.get(pk=member_id)
        project_id = member.proj.pk

        if (member.proj.admin != request.user):
            return HttpResponseForbidden('Access Denied')
        helpers.MemberDelete(member)
        return redirect('cyka:project_team', project_id)

    except Member.DoesNotExist:
        raise Http404("Member does not exist")
        
"""
edit view of member
"""
@login_required
def member_edit(request, member_id):
    try:
        member = Member.objects.get(pk=member_id)
        priority_list = member.priority_set.all().order_by('priority')

        if len(priority_list) == 0:
            priority_list = create_priority_list(member)

    except Member.DoesNotExist:
        raise Http404("Member does not exist")
    
    if request.method == 'POST':
        member_form = MemberForm(request.POST)
        if member_form.is_valid():
            member_form = MemberForm(request.POST, instance=member)
            member = member_form.save(commit=False)
            member.save()
        ok_form = MemberOkForm(request.POST)
        if ok_form.is_valid():
            ok_form = MemberOkForm(request.POST, instance=member)
            member = ok_form.save(commit=False)
            member.save()
    else:
        ok_form = MemberOkForm(instance=member)
        member_form = MemberForm(instance=member)
    return render(request, 'cyka/member_edit.html', {'project' : member.proj, 'member': member, 'priority_list':priority_list, 'ok_form' : ok_form, 'member_form' : member_form })

@login_required
def agenda(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    members = project.member_set.all()
    struct = Structure.factory(project.ptype)
    err_text = ""
    for m in members:
        if m.status == False:
            err_text = "Es haben noch nicht alle Teilnhemer ihre Themenliste bestätigt"
            break;
    if len(members)< struct.getMinPersons():
        err_text = "Minimale Anzahl von " + str(struct.getMinPersons()) + " Teilnehmern noch nicht erreicht"
    if err_text != "":
        #do not create agenda
        return render(request, 'cyka/project_agenda_err.html', {'project' : project, 'err_text' : err_text})
    #create agenda
    a = Agenda(project)
    agenda = a.get_agenda()
    return render(request, 'cyka/project_agenda.html', {'project' : project, 'agenda' : agenda })



@login_required
def project_team(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    struct = Structure.factory(project.ptype)
    return render(request, 'cyka/project_team.html', {'project' : project, 'min' : struct.getMinPersons(), 'max' : struct.getMaxPersons() })
    
@login_required
def project_topics(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
        topics = project.topic_set.all()
        if len(topics) == 0:
            topics = create_topics(project)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    return render(request, 'cyka/project_topics.html', {'project' : project })
   
@login_required
def project_list(request):
    projects = Project.objects.all().filter(admin=request.user)
    return render(request, 'cyka/project_list.html', {'projects': projects})

@login_required
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

@login_required
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
prj:    database object Project

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

def personal_edit_up(request, uuid, priority):
    try:
        member = Member.objects.all().filter(uuid=uuid)[0]
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

    return redirect('cyka:personal_edit', uuid)

def personal_agenda(request, uuid):
    try:
        member = Member.objects.all().filter(uuid=uuid)[0]

    except Member.DoesNotExist:
        raise Http404("Member does not exist")
    return render(request, 'cyka/personal_agenda.html', {'project' : member.proj, 'member': member})

def personal_edit(request, uuid):
    try:
        member = Member.objects.all().filter(uuid=uuid)[0]
        priority_list = member.priority_set.all().order_by('priority')

        if len(priority_list) == 0:
            priority_list = create_priority_list(member)

    except Member.DoesNotExist:
        raise Http404("Member does not exist")
    
    if request.method == 'POST':
        member_form = MemberForm(request.POST)
        ok_form = MemberOkForm(request.POST)
        if ok_form.is_valid():
            ok_form = MemberOkForm(request.POST, instance=member)
            member = ok_form.save(commit=False)
            member.save()
    else:
        ok_form = MemberOkForm(instance=member)
    return render(request, 'cyka/personal_edit.html', {'project' : member.proj, 'member': member, 'priority_list':priority_list, 'ok_form' : ok_form})

