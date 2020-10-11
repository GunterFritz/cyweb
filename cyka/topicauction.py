import json
from lib.structure import Structure2 as Structure
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Member, Topic, Table, Card, SIsign
from .config import Jitsi, Pad
from . import helpers
from .workflow import Workflow
from django.db import transaction
from django.utils.safestring import SafeString

"""
File to render the topicauction
"""

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
    
    @staticmethod
    def getProjAsi(proj, tid = None):
        tables = proj.table_set.all() if tid == None else proj.table_set.all().filter(id=tid)
        n = Structure.factory(proj.ptype).getMinAgreedPersons(len(proj.member_set.all().filter(mtype='M')))
        htables = []
        for t in tables:
            h = HTMLAsi(t,n)
            if h.progress == 100:
                htables.append(h)
        
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
            return {'id': self.member.id, 'member_votes_left':v, 'max_votes': n}
        
        tables = []

        for h in htables:
            mtv = self.numVotes(h.table)
            tables.append({ 'id':h.table.id, 'voted':h.votes, 'mvoted':mtv })
        
        return {'member_votes_left':v, 'max_votes': n, 'table': tables}

    def get_priority_list(self):
        priority_list = self.member.priority_set.all().order_by('priority')

        if len(priority_list) > 0:
            return priority_list

        topics =  self.member.proj.topic_set.all()
        if len(topics) == 0:
            return None
        i=0
        for t in topics:
            self.member.priority_set.create(priority=i, topic=t)
            i=i+1

        return self.priority_set.all()
    

    #def create_priority_list(self):
    #    topics =  self.member.proj.topic_set.all()
    #    if len(topics) == 0:
    #        return None
    #    i=0
    #    for t in topics:
    #        self.member.priority_set.create(priority=i, topic=t)
    #        i=i+1
    #
    #    return self.member.priority_set.all()

#Member pages

"""
class to render the Topic creation step

"""
class AgreedStatementImportance(helpers.MemberRequest):
    def __init__(self, request, uuid):
        helpers.MemberRequest.__init__(self,request, uuid)
        self.table = None
        self.step = Workflow.getStep(self.member.proj, 80, self.request)

    
    def get(self):
        table_id = self.request.GET.get('table', '')
        if table_id != 'all':
            self.table = helpers.get_asi(table_id, self.member.proj)
        func = self.request.GET.get('function', '')
        
        #votes
        if func == 'votes':
            return self.getVotes()
        
        html_mem = HTMLMember(self.member)
        v = html_mem.getMaxVotes()
        
        pad = Pad(self.table.uuid, self.member.name)
        asis = self.table.sisign_set.all()
       
        tables = []
        tables.append(HTMLAsi(self.table))
        data = HTMLMember(self.member).getVotesJson(tables)

        #main page
        return render(self.request, 'topicauction/member_join_asi.html', {
            'project' : self.member.proj, 
            'member': self.member, 
            "etherpad": pad, 
            "supporter": asis,
            'asi': HTMLAsi(self.table, 0),
            'table': self.table, 
            'votes':range(v),
            'json_votes':SafeString(json.dumps(data))
            })

    def post(self):
        table_id = self.request.POST.get('table', '')
        self.table = helpers.get_asi(table_id, self.member.proj)
        func = self.request.POST.get('function', '')
        
        #don't vote, when step isn't started
        if self.step.isActive():
            if(func == "plus"):
                HTMLMember(self.member).vote(self.table)
            if(func == "minus"):
                HTMLMember(self.member).unvote(self.table)

        return self.getVotes()

    """
       returns json for all asi
    """
    def getVotesJson(self):
        hm = HTMLMember(self.member)
        n = hm.getMaxVotes()
        v = hm.getFreeVotes()
        
        tables = []

        if self.table != None:
            mtv = hm.numVotes(self.table)
            tv = len(self.table.asivotes_set.all())
            tables.append({ 'id':self.table.id, 'voted':tv, 'mvoted':mtv })
        else:
            for table in self.member.proj.table_set.all():
                mtv = hm.numVotes(table)
                tv = len(table.asivotes_set.all())
                tables.append({ 'id':table.id, 'voted':tv, 'mvoted':mtv })
        
        return {'member_votes_left':v, 'max_votes': n, 'table': tables}
    
    """
       returns json for specific asi
    """
    def getVotes(self):
        if self.table != None:
            tables = []
            tables.append(HTMLAsi(self.table))
            data = HTMLMember(self.member).getVotesJson(tables)
        else:
            data = HTMLMember(self.member).getVotesJson(HTMLAsi.getProjAsi(self.member.proj))
        return JsonResponse(data, safe=False)

"""
renders all asi for that can be voted
the basic view shows all tables
GET: render page with all tables
"""
class ASIOverview(helpers.MemberRequest):
    def __init__(self, request, uuid):
        helpers.MemberRequest.__init__(self,request, uuid)

    def get(self):
        func = self.request.GET.get('function', '')
        
        #votes
        if func == 'priority_list':
            return self.renderPriority()
        
        return self.overview()
    
    def overview(self):
        #table_id = self.request.GET.get('table', '')
        page = int(self.request.GET.get('page', 1))
        
        #render tables overview
        step = Workflow.getStep(self.member.proj, 80, self.request)
        
        htables = HTMLAsi.getProjAsi(self.member.proj)
        
        #ceil (instead of math.ceil)
        pages = int(len(htables)/6) + 1
        if len(htables) % 6 > 0:
            pages = pages + 1
        
        html_mem = HTMLMember(self.member)
        v = HTMLMember(self.member).getMaxVotes()
        data = HTMLMember(self.member).getVotesJson(HTMLAsi.getProjAsi(self.member.proj))
        
        return render(self.request, 'topicauction/member_asi_overview.html', {'project' : self.member.proj, 
            'member': self.member, 
            'tables': htables,
            'tables': htables[(page-1)*6:page*6], 
            'pages': range(1, pages), 
            'page':page,
            'votes':range(v),
            'json_votes':SafeString(json.dumps(data)),
            'step': step})

    def renderPriority(self):
        html_mem = HTMLMember(self.member)
        prio = html_mem.get_priority_list()
        
        return render(self.request, 'topicauction/member_priority_list.html', {
            'project' : self.member.proj, 
            'member': self.member, 
            'priority_list': prio
            })



#moderator pages
class ModeratorScheduler(helpers.ModeratorRequest):
    def __init__(self, request, pid):
        helpers.ModeratorRequest.__init__(self,request, pid)
        #wf post request is handled by workflow itself
        self.step = Workflow.getStep(self.proj, 80, request)
    
    def post(self):
        return render(self.request, 'topicauction/moderator_scheduler.html', {'project' : self.proj, 'step': self.step })
    
    def get(self):
        function = self.request.GET.get('function', '')
    
        #show sorted (by votes) list of ASIs
        if function == 'table':
            return self.renderTable()
        
        #get details page of an ASI
        if function == 'join':
            m = ModeratorJoinASI(self.request, self.proj)
            return m.renderJoinAsi()
        
        #show votes of members
        if function == 'member':
            return self.renderMember()
        
        #get votes of members as json
        if function == 'updatemember':
            data = self.jsonMember()
            return JsonResponse(data, safe=False)
        
        #get sorted list (by votes) of ASIs
        if function == 'updatetable':
            tid = self.request.GET.get('table', '')
            if tid == '':
                tid = None
            data = HTMLAsi.getProjAsiJson(self.proj, tid)
            return JsonResponse(data, safe=False)
        
        if function == 'createtopics':
            return self.createTopics()
        
        #scheduling page requested
        return render(self.request, 'topicauction/moderator_scheduler.html', {'project' : self.proj, 'step': self.step })

    """
    the function creates from the first ASIs topics
    """
    def createTopics(self):
        #TODO check current step, must not be created/ deleted when step is finished or assignment is already finished
        num = Structure.factory(self.proj.ptype).getNumTopics()
        asi = sorted(HTMLAsi.getProjAsi(self.proj), key=lambda HTMLAsi: HTMLAsi.votes, reverse=True)
        if num > len(asi):
            return None
        
        #delete old topics
        self.proj.topic_set.all().delete()
        
        #create new
        for i in range(1, num +1):
            topic = self.proj.topic_set.create(number=i, asi=asi[i-1].table, name=asi[i-1].name, desc=asi[i-1].table.card.desc)
    
        return self.renderTable()

    def jsonMember(self):
        retval = []
        for m in self.proj.member_set.all().filter(mtype='M'):
            retval.append(HTMLMember(m).getVotesJson())

        return {'member':retval}

    def renderMember(self):
        data = self.jsonMember()
        mem = HTMLMember.getProjMember(self.proj)

        return render(self.request, 'topicauction/moderator_member_overview.html', {'project' : self.proj, 
            'member' : mem,
            'votes' : range(HTMLMember.getNumVotes(self.proj)),
            'json_member':SafeString(json.dumps(data))
            })
            
    def renderTable(self):
        data = HTMLAsi.getProjAsiJson(self.proj)
        t = HTMLAsi.getProjAsi(self.proj)

        return render(self.request, 'topicauction/moderator_asi_sorted.html', {'project' : self.proj, 
            'table' : sorted(t, key=lambda HTMLAsi: HTMLAsi.votes, reverse=True),
            'count': range(len(t)),
            'threshold' : Structure.factory(self.proj.ptype).getNumTopics(),
            'json_table':SafeString(json.dumps(data))
            })

class ModeratorJoinASI:
    def __init__(self, request, proj):
        self.request = request
        table_id = self.request.GET.get('table', '')
        self.table = Table.objects.get(pk=table_id)
        self.name = self.request.user.get_username
        self.proj = proj
    
    def renderJoinAsi(self):
        pad = Pad(self.table.uuid, self.request.user.get_username)
        pad.setReadOnly()
        asis = self.table.sisign_set.all()
        data = HTMLAsi.getProjAsiJson(self.proj, self.table.id)
        
        return render(self.request, 'topicauction/moderator_join_asi.html', {
            'project' : self.proj, 
            "etherpad": pad, 
            "supporter": asis,
            'asi': HTMLAsi(self.table, 0),
            'table': self.table, 
            'json_votes':SafeString(json.dumps(data))
            })

