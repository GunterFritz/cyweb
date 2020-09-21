from lib.structure import Structure2 as Structure
from .models import Project, Topic, Member, Assignment, Card, Table

def MemberDelete(member):
    member.priority_set.all().delete()
    member.assignment_set.all().delete()
    member.cardvotes_set.all().delete()
    member.delete()

def CardDelete(card):
    card.cardvotes_set.all().delete()

def ProjectDelete(project):
    for c in card.card_set.all():
        CardDelete(m)
    for m in project.member_set.all():
        MemberDelete(m)
    project.topic_set.all().delete()
    project.workflowelement_set.all().delete()
    project.delete()

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


#obsolete?
"""
class HtmlPerson:
    def __init__(self, db):
        self.ty = db.atype
        self.name = db.member.name
        p = db.member.priority_set.all().filter(topic=db.topic)[0]
        self.priority = p.priority

class HtmlTopic:
    def __init__(self, db):
        self.topic = db
        self.person = []
        assignments =  db.assignment_set.all()

        for a in assignments:
            self.person.append(HtmlPerson(a))
"""

class Agenda:
    def __init__(self, proj):
        self.project = proj

        if not self.project.hasagenda:
            self.create_agenda()

    """
    creates the agenda
    """
    def create_agenda(self):
        #struct = Structure.factory(proj.ptype)
        struct = Structure.factory("O")
        struct.array_init(self.create_if_list())
        struct.build()

        i=1
        for t in struct.getAgenda():
            self.assign_topic(t[0], i)
            self.assign_topic(t[1], i+1)
            i = i + 2
    """
    creates the assignments for one topic from a "flat" algorithm object
    ---
    params:
        t Edge object
        num possition in agenda
    """
    def assign_topic(self, t, num):
        db_topic =  self.project.topic_set.all().filter(number=t.topic.index)[0]

        #clean existing assignment
        db_topic.assignment_set.all().delete()

        db_topic.agendanumber = num
        db_topic.color = t.color
        #recreate assignment
        for p in t.getPersons():
            person = Member.objects.get(pk=p.name)
            db_topic.assignment_set.create(member=person, atype="M")
            db_topic.save()

    #returns the priority for a person as list
    def get_priority_list(self, person):
        plist = person.priority_set.all().order_by('priority')
        retval = [person.id]
        for p in plist:
            retval.append(p.topic.number)
        return retval

    #creates an array that can be used as input for structure object
    def create_if_list(self):
        retval = []
        for p in self.project.member_set.all():
            retval.append(self.get_priority_list(p))
        return retval

    """
    creates a good readable structure from db objects
    """
    def get_agenda(self):
        topics =  self.project.topic_set.all().order_by('agendanumber')
        agenda = []
        i = 0
        while i < len(topics):
            agenda.append([HtmlTopic(topics[i]), HtmlTopic(topics[i+1])])
            i = i + 2

        return agenda

"""
html wrapper a card for a specific person
checks if voted, can vote or unvote a card
"""
class HtmlCard:
    def __init__(self, mc, member):
        self.model = mc
        self.member = member
        self.voted = False
       
        #check if member has voted a card
        v = self.member.cardvotes_set.filter(card=self.model.id)
        if len(v) == 0:
            #not voted
            self.voted = False
        else:
            #voted
            self.voted = True
        
        #count votes
        self.votes = len(self.model.cardvotes_set.all())

    """
    votes a card if unvoted, unvote it voted 
    """
    def vote(self):
        v = self.member.cardvotes_set.filter(card=self.model.id)
        
        if len(v) == 0:
            #create a vote
            self.member.cardvotes_set.create(card=self.model)
            self.voted = True
        else:
            #delete vote
            v[0].delete()
            self.voted = False
        
        self.votes = len(self.model.cardvotes_set.all())

class MemberRequest:
    def __init__(self, request, uuid):
        #TODO refactor: uuid as url param
        self.member = get_member_by_uuid(uuid)
        self.request = request

    def process(self):
        if self.request.method == 'GET':
            return self.get()
    
        if self.request.method == 'POST':
            return self.post()

        return None

class ModeratorRequest:
    def __init__(self, request, pid):
        self.proj = get_project(request, pid)
        self.request = request

    def process(self):
        if self.request.method == 'GET':
            return self.get()
    
        if self.request.method == 'POST':
            return self.post()

        return None

def get_card(card_id, member):
    card = Card.objects.get(pk=card_id)
    if card.member == member:
        return card
    else:
        raise Http404("No such card")
        
def get_asi(tableid, proj):
    try:
        table = Table.objects.get(pk=tableid)
    except Table.DoesNotExist:
        raise Http404("No such table")
    
    if table.proj != proj:
        raise Http404("No such table")

    return table
