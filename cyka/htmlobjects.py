import json
from random import randrange 
from lib.structure import Structure2 as Structure
from .models import Member, Table, Card, SIsign
from . import helpers

"""
File to render the topicauction
"""
class HTML_Si:
    def __init__(self, card):
        self.card = card
        self.asi = len(card.table_set.all())

    @staticmethod
    def get_proj_si(proj):
        si = []
        for c in proj.card_set.all():
            si.append(HTML_Si(c))

        return si

#wrapper
class HTMLAsi:
    #table: DB Object
    #num: threshold of supporters to make an asi
    def __init__(self, table, num = 0):
        self.table = table
        self.name = self.table.card.heading
        self.supporter = len(self.table.sisign_set.all())
        self.progress = 100
        self.max = num
        if self.supporter < num:
            self.progress = int(self.supporter*100/num)
        self.votes = len(self.table.asivotes_set.all())

    def to_json(self):
        return {
            'id': self.table.id,
            'cardid': self.table.card.id,
            'name': self.name,
            'desc': self.table.card.desc,
            'progress' : self.progress,
            'votes' : self.votes
        }
    
    """
    returns a specific HTMLAsi, or if no id is given all
    params
        tid: table_id, 
    """
    @staticmethod
    def get_proj_asi_id(proj, tid = None):
        tables = proj.table_set.all() if tid == None else proj.table_set.all().filter(id=tid)
        n = Structure.factory(proj.ptype).getMinAgreedPersons(len(proj.member_set.all().filter(mtype='M')))
        htables = []
        for t in tables:
            h = HTMLAsi(t,n)
            if h.progress == 100:
                htables.append(h)
        
        return htables

    """
    returns all project asi
    ---
    params
    agreed: bool, if true, return only agreed
    json: bool, if true return asi as json
    """
    def get_proj_asi(proj, agreed=False, json=False):
        tables = proj.table_set.all()
        n = Structure.factory(proj.ptype).getMinAgreedPersons(len(proj.member_set.all().filter(mtype='M')))
        htables = []
        for t in tables:
            if agreed == "true":
                h = HTMLAsi(t,n)
                if h.progress == 100:
                    if json:
                        htables.append(h.to_json())
                    else:
                        htables.append(h)
            else:
                if json:
                    htables.append(HTMLAsi(t,n).to_json())
                else:
                    htables.append(HTMLAsi(t,n))

        return htables
    
    """
    returns all ASI of a project in json
    ---
    params
      proj Model.Project

    return
      dictonary
    """
    @staticmethod
    def getProjAsiJson(proj, tid = None):
        t = HTMLAsi.getProjAsi(proj, tid)
        retval = []
        i = 0
        for e in sorted(t, key=lambda HTMLAsi: HTMLAsi.votes, reverse=True):
            retval.append({'id': e.table.id, 'name': e.name, 'votes': e.votes, 'sort': i})
            i = i + 1

        return { 'asi': retval }

class PrioList:
    def __init__(self, member):
        class P:
            def __init__(self, t, a):
                self.topic = t
                self.assigned = a
        self.plist = []
        assignment =  member.assignment_set.all()
        for p in member.priority_set.all().order_by('priority'):
            a = False
            if len(assignment) > 0:
                if p.topic == assignment[0].topic or p.topic == assignment[1].topic:
                    a = True
            self.plist.append(P(p.topic,a))


class HTMLMember:
    def __init__(self, member):
        self.member = member

    @staticmethod
    def getProjMember(proj):
        member = proj.member_set.all().filter(mtype='M')
        retval = []
        for m in member:
            retval.append(HTMLMember(m))
        
        return retval
    
    @staticmethod
    def getNumVotes(proj):
        return Structure.factory(proj.ptype).getNumTopics()

    def getFreeVotes(self):
        votes = self.member.asivotes_set.all()
        n_votes = Structure.factory(self.member.proj.ptype).getNumTopics()
        
        return n_votes - len(votes)

    def getMaxVotes(self):
        return Structure.factory(self.member.proj.ptype).getNumTopics()
    
    @staticmethod
    def jsonMember(proj):
        retval = []
        for m in proj.member_set.all().filter(mtype='M'):
            retval.append(HTMLMember(m).getVotesJson())

        return {'member':retval}


    #creates a vote relation between member and asi
    def vote(self, asi):
        if self.getFreeVotes() < 1:
            return 0
        
        self.member.asivotes_set.create(table=asi)

        return self.getFreeVotes()
    
    #deletes a vote relation between member and asi
    def unvote(self, asi):
        votes = self.member.asivotes_set.all().filter(table=asi)

        if len(votes) > 0:
            votes[0].delete()

    def numVotes(self, asi):
        return len(self.member.asivotes_set.all().filter(table=asi))
    
    #creates json message with votes from a memmber
    def getVotesJson(self, htables = None):
        n = self.getMaxVotes()
        v = self.getFreeVotes()

        if htables == None:
            return {'id': self.member.id, 'member_votes_left':v, 'max_votes': n, 'status': self.member.status}
        
        tables = []

        for h in htables:
            mtv = self.numVotes(h.table)
            tables.append({ 'id':h.table.id, 'voted':h.votes, 'mvoted':mtv })
        
        return {'member_votes_left':v, 'max_votes': n, 'table': tables}

    """
    creates a by personal priorities sorted list with ASIs
        assignments =  db.assignment_set.all()
    """
    def get_priority_list(self):
        priority_list = self.member.priority_set.all().order_by('priority')

        if len(priority_list) > 0:
            return PrioList(self.member)

        topics =  self.member.proj.topic_set.all()
        if len(topics) == 0:
            return None
        i=0
        for t in topics:
            self.member.priority_set.create(priority=i, topic=t)
            i=i+1

        #secure,that each member has its own priority
        self.shuffle_priority_list()
        
        return PrioList(self.member)
        return self.member.priority_set.all().order_by('priority')
   
    """
    create a random order for priority list
    needed for easier testing, to secure, that each member has its own sorting
    """
    def shuffle_priority_list(self):
        priority_list = self.member.priority_set.all().order_by('priority')
        #shuffle
        for p in priority_list:
            p1 = randrange(priority_list.count())
            p2 = p.priority
        
            #switch to priorities
            p.priority = priority_list[p1].priority
            p.save()
            priority_list[p1].priority = p2
            priority_list[p1].save()

