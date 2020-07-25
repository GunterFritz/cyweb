from lib.structure import Structure2 as Structure
from lib.structure import Topic as A_Topic
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect,HttpResponse,HttpResponseForbidden, Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import CardForm, ProjectForm, TopicForm, MemberForm, MemberOkForm, WorkflowElementForm
from .models import Project, Topic, Member, Assignment, Card
from random import randrange 
from . import helpers
from .helpers import Agenda, HtmlCard
from .workflow import Workflow
from .config import Jitsi

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
    proj = get_project(request, project_id)
    step = Workflow.getStep(proj, 10, request)
    
    if request.method == 'POST':
        if 'workshop' in request.POST:
            form = ProjectForm(request.POST)
            if form.is_valid():
                form.save(proj)
                proj.save()
        else:
            form = ProjectForm(initial={'name': proj.name, 'question' : proj.question, 'ptype' : proj.ptype })
    else:
        form = ProjectForm(initial={'name': proj.name, 'question' : proj.question, 'ptype' : proj.ptype })
    return render(request, 'cyka/project_details.html', {'project' : proj, 'form': form, 'step': step, 'wf_form': step.form })

@login_required
def member_new(request, project_id):
    project = get_project(request, project_id)
    
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            member = form.save()
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
        proj = get_project(request, project_id)

        if (proj.admin != request.user):
            return HttpResponseForbidden('Access Denied')
        helpers.ProjectDelete(proj)
        
        return redirect('cyka:project_list')

    except Member.DoesNotExist:
        raise Http404("Project delete error")

@login_required
def member_delete(request, member_id):
    member = get_member(request, member_id)
    project_id = member.proj.pk

    helpers.MemberDelete(member)
    return redirect('cyka:project_team', project_id)

"""
edit view of member
"""
@login_required
def member_edit(request, member_id):
    member = get_member(request, member_id)
    priority_list = member.priority_set.all().order_by('priority')

    if len(priority_list) == 0:
        priority_list = create_priority_list(member)

    if request.method == 'POST':
        member_form = MemberForm(request.POST)
        if member_form.is_valid():
            member = member_form.save(member)
            member.save()
        ok_form = MemberOkForm(request.POST)
        if ok_form.is_valid():
            ok_form = MemberOkForm(request.POST, instance=member)
            member = ok_form.save(commit=False)
            member.save()
    else:
        ok_form = MemberOkForm(instance=member)
        member_form = MemberForm(initial={'name': member.name, 'email' : member.email, 'mtype' : member.mtype })
    return render(request, 'cyka/member_edit.html', {'project' : member.proj, 'member': member, 'priority_list':priority_list, 'ok_form' : ok_form, 'form' : member_form })

@login_required
def agenda(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    members = project.member_set.all().filter(mtype='M')
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
    proj = get_project(request, project_id)
    step = Workflow.getStep(proj, 20, request)
    struct = Structure.factory(proj.ptype)
    
    return render(request, 'cyka/project_team.html', {'project' : proj, 'min' : struct.getMinPersons(), 'max' : struct.getMaxPersons(), 'step' : step, 'wf_form' : step.form })

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
def topic_toggle(request, topic_id):
    try:
        topic = Topic.objects.get(pk=topic_id)
    except Topic.DoesNotExist:
        raise Http404("Topic does not exist")

    topic.is_active = not topic.is_active
    topic.save()
    
    a = Agenda(topic.proj)
    agenda = a.get_agenda()
    return render(request, 'cyka/project_agenda.html', {'project' : topic.proj, 'agenda' : agenda })

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
    form = None
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            prj = form.save()
            prj.admin = request.user
            prj.save()
            create_topics(prj)
        #return redirect('cyka:project_list', pk=post.pk)
            return redirect('cyka:project_list')
    else:
        form = ProjectForm()
    return render(request, 'cyka/project_new.html', {'form': form})


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

"""
------------personal requests-------------
"""

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

def personal_plenum(request, uuid):
    try:
        member = Member.objects.all().filter(uuid=uuid)[0]

    except Member.DoesNotExist:
        raise Http404("Member does not exist")
    return render(request, 'cyka/personal_plenum.html', {'project' : member.proj, 'member': member})

def test(request, uuid):
    member = Member.objects.all().filter(uuid=uuid)[0]
    return render(request, 'cyka/test2.html', {'project' : member.proj, 'member': member})

"""
get_more_agenda reloads the agenda, called for ajax

params
-------
uuid: uuid from member
"""
def get_more_agenda(request, uuid):
    member = get_member_by_uuid(uuid)
    wf = Workflow.get(member.proj, False)
    return render(request, 'cyka/get_more_agenda.html', {'project' : member.proj, 'member': member, 'workflow': wf})

def personal_votes(request, uuid):
    member = get_member_by_uuid(uuid)
    page = int(request.GET.get('page', 1))
    step = Workflow.getStep(member.proj, 50, request)

    cards = member.proj.card_set.all()
    #ceil (instead of math.ceil)
    pages = int(len(cards)/6) + 1
    if len(cards) % 6 > 0:
        pages = pages + 1
    
    vote = request.GET.get('vote', None)
    if vote != None:
        # check if card exists
        try:
            card = Card.objects.get(pk=vote)
        except Card.DoesNotExist:
            raise Http404("No such card")
        HtmlCard(card, member).vote()

    hcards = []
    for c in cards[(page-1)*6:page*6]:
        hcards.append(HtmlCard(c, member))

    return render(request, 'cyka/personal_votes.html', {'project' : member.proj, 'member': member, 'cards': hcards, 'pages': range(1, pages), 'page':page, 'step': step})

def personal_card(request, uuid):
    member = get_member_by_uuid(uuid)
    step = Workflow.getStep(member.proj, 40, request)
        
    #card added, deleted or changed 
    if request.method == 'POST':
        #get action
        card_id = request.POST.get('cardid', '')
        delete = request.POST.get('delete', 'false')
        card = None
        if card_id != '':
            card = get_card(card_id, member)
        #delete action
        if delete == 'true' and card != None:
            card.delete()
        #new and save actions
        else:
            form = CardForm(request.POST)
            if form.is_valid():
                card = form.save(card)
                card.proj = member.proj
                card.member = member
                card.save()
            else:
                #input fields not valid
                return render(request, 'cyka/add_card.html', {'project' : member.proj, 'member': member, 'form': form})
        cards = member.card_set.all()
        #return to overview
        return render(request, 'cyka/personal_cards.html', {'project' : member.proj, 'member': member, 'cards': cards, 'step': step})

    card_id = request.GET.get('card', '')
    if card_id == 'new':
        form = CardForm()
        return render(request, 'cyka/add_card.html', {'project' : member.proj, 'member': member, 'form': form})
    if card_id == '':
        cards = member.card_set.all()

        return render(request, 'cyka/personal_cards.html', {'project' : member.proj, 'member': member, 'cards': cards, 'step': step})
    
    card = get_card(card_id, member)
    form = CardForm(initial={'heading': card.heading, 'desc' : card.desc, 'cardid': card.id })
    return render(request, 'cyka/add_card.html', {'project' : member.proj, 'member': member, 'form': form})

def personal_workflow(request, uuid):
    member = get_member_by_uuid(uuid)
    wf = Workflow.get(member.proj, False)
    
    jitsi = Jitsi(member.proj.uuid, "Plenum", member.name)
    
    return render(request, 'cyka/personal_agenda.html', {'project' : member.proj, 'member': member, 'workflow': wf, 'jitsi': jitsi })

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

@login_required
def admin_votes(request, project_id):
    proj = get_project(request, project_id)
    step = Workflow.getStep(proj, 50, request)
    
    
    return render(request, 'cyka/admin_jostle.html', {'project' : proj, 'step': step, 'wf_form': step.form })

@login_required
def admin_jostle(request, project_id):
    proj = get_project(request, project_id)
   
    #change status of step
    if request.method == 'POST':
        step_id = request.POST['step']
        step = Workflow.getStep(proj, int(step_id), request)
    
        return render(request, 'cyka/admin_jostle_step.html', {'project' : proj, 'step': step, 'wf_form': step.form })
    
    
    function = request.GET.get('function', '')
    #agenda page requested
    if function == 'agenda':
        jostle_section = Workflow.get(proj)[1]
        return render(request, 'cyka/admin_jostle_agenda.html', {'project' : proj, 'section': jostle_section })
    
    #step details requested
    if function == 'step':
        step_id = request.GET.get('stepid', '')
        step = Workflow.getStep(proj, int(step_id), request)
    
        return render(request, 'cyka/admin_jostle_step.html', {'project' : proj, 'step': step })
    
    #initalization
    jitsi = Jitsi(proj.uuid, "Plenum", request.user.get_username)
    
    return render(request, 'cyka/admin_jostle.html', {'project' : proj, 'jitsi': jitsi })

@login_required
def admin_brainwriting(request, project_id):
    proj = get_project(request, project_id)
    step = Workflow.getStep(proj, 40, request)
    
    return render(request, 'cyka/admin_brainwriting.html', {'project' : proj, 'step': step, 'wf_form': step.form })

@login_required
def jostle_welcome(request, project_id):
    proj = get_project(request, project_id)
    step = Workflow.getStep(proj, 30, request)
    
    return render(request, 'cyka/jostle_welcome.html', {'project' : proj, 'step': step, 'wf_form': step.form })

@login_required
def rand_session(request, project_id):
    proj = get_project(request, project_id)
    step = Workflow.getStep(proj, 60, request)
    
    members = proj.member_set.all().filter(mtype='M')
    
    if request.method == 'POST':
        #session started
        username = request.POST['play']
        step.toggleState()
        return render(request, 'cyka/play.html', {'project' : proj, 'step': step})

    #assign each member to a group
    num = int(len(members)/4) 
    groups = [[] for _ in range (num)]
    i=0
    for i in range(len(members)):
        groups[i % num].append(members[i])

    jitsi = Jitsi(proj.uuid, "Plenum", request.user.get_username)
    
    return render(request, 'cyka/admin_rand_sessions.html', {'project' : proj, 'step': step, 'wf_form': step.form, 'groups': groups, 'jitsi': jitsi })

@login_required
def plenum(request, project_id):
    proj = get_project(request, project_id)
    
    return render(request, 'cyka/project_plenum.html', {'project' : proj})

@login_required
def workflow(request, project_id):
    proj = get_project(request, project_id)
    wf = Workflow.get(proj)
    
    return render(request, 'cyka/workflow.html', {'project' : proj, 'workflow': wf})

"""
------------common requests-------------
"""
"""
edit or create an table
"""
def table(request, project_id):
    table = None
    try:
        project = Project.objects.get(pk=project_id)
        table_id = request.GET.get('table', '')
        #Todo check member
        member = request.GET.get('table', '')
        if table == '':
            raise Http404("No table")
        if table_id != 'new':
            table = Topic.objects.get(pk=table_id)
    except Project.DoesNotExist:
        raise Http404("Project or table does not exist")


    
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)
            table.proj = project
            table.save()
        return redirect('cyka:project_team', project_id)
    else:
        table = MemberForm()
    return render(request, 'cyka/member_add.html', {'project' : project, 'form' : form })


"""
join room as common function
"""

@login_required
def join_room(request, uuid):
    project_id = request.GET.get('project', '')
    proj = get_project(request,project_id)
    subject = None
    if str(proj.uuid) == str(uuid):
        subject = "Plenum"
    jitsi = Jitsi(uuid, subject, request.user.get_username)
    return render(request, 'cyka/room.html', {'jitsi' : jitsi, 'moderator' : True , 'param' : project_id})

"""
join room as common function without login
"""
def join_room_member(request, uuid):
    project_id = request.GET.get('project', '')
    muuid = request.GET.get('muuid', '')
    proj = get_project(request, project_id, False)
    member = proj.member_set.all().filter(uuid=muuid)
    if len(member) < 1:
        raise Http404("No such member")
    
    subject = get_subject(proj, uuid)
    jitsi = Jitsi(uuid, subject, member[0].name)
    return render(request, 'cyka/room.html', {'jitsi' : jitsi, 'moderator' : False , 'param' : project_id})
"""
calculates the subject of jitsi meet room (display name for room)
"""
def get_subject(proj, uuid):
    subject = None
    if str(proj.uuid) == str(uuid):
        subject = "Plenum"
    else:
        topics = proj.topic_set.all().filter(uuid=uuid)
        if len(topics) > 0:
            subject = topics[0].name

    return subject

"""
returns member to an id and checks, if user has authorization

params
------
request: http request
pid: privat key of member

return
------
Models.Member
"""
def get_member(request, mid):
    try:
        member = Member.objects.get(pk=mid)
    except Member.DoesNotExist:
        raise Http404("No such member")
    
    if (member.proj.admin != request.user):
        raise Http404("No such member")
    
    return member

def get_card(card_id, member):
    card = Card.objects.get(pk=card_id)
    if card.member == member:
        return card
    else:
        raise Http404("No such card")

"""
returns member to an id 

params
------
uuid: uuid of member
proj_id (optional, not used)

return
------
Models.Member
"""
def get_member_by_uuid(uuid, proj_id = None):
    try:
        member = Member.objects.all().filter(uuid=uuid)[0]
    except Member.DoesNotExist:
        raise Http404("No such member")

    return member
"""
returns project to an id and checks, if user has authorization

params
------
request: http request
pid: privat key of project

return
------
Models.Project
"""
def get_project(request, pid, auth = True):
    try:
        project = Project.objects.get(pk=pid)
    except Project.DoesNotExist:
        raise Http404("No workshop")
    
    if (auth and project.admin != request.user):
        raise Http404("No workshop")
    
    return project

