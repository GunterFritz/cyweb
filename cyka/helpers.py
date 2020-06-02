from lib.structure import Structure2 as Structure
from .models import Project, Topic, Member, Assignment

def MemberDelete(member):
    member.priority_set.all().delete()
    member.assignment_set.all().delete()
    member.delete()

def ProjectDelete(project):
    for m in project.member_set.all():
        MemberDelete(m)
    project.topic_set.all().delete()
    project.workflowelement_set.all().delete()
    project.delete()

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

