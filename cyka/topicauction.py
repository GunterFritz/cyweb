from lib.structure import Structure2 as Structure
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Member, Table, Card, SIsign
from .config import Jitsi, Pad
from . import helpers
from .workflow import Workflow
from django.db import transaction


"""
File to render the topicauction
"""

#wrapper
class HTMLAsi:
    #table: DB Object
    #num: threshold of supporters to make an asi
    def __init__(self, table, num):
        self.table = table
        self.supporter = len(self.table.sisign_set.all())
        self.progress = 100
        self.max = num
        if self.supporter < num:
            self.progress = int(self.supporter*100/num)
        self.votes = len(self.table.asivotes_set.all())
    
    @staticmethod
    def getProjAsi(proj):
        tables = proj.table_set.all()
        n = Structure.factory(proj.ptype).getMinAgreedPersons(len(proj.member_set.all().filter(mtype='M')))
        htables = []
        for t in tables:
            h = HTMLAsi(t,n)
            if h.progress == 100:
                htables.append(h)
        
        return htables

class HTMLMember:
    def __init__(self, member):
        self.member = member

    def getFreeVotes(self):
        votes = self.member.asivotes_set.all()
        n_votes = Structure.factory(self.member.proj.ptype).getNumTopics()
        
        return n_votes - len(votes)

    def getMaxVotes(self):
        return Structure.factory(self.member.proj.ptype).getNumTopics()

    def vote(self, asi):
        if self.getFreeVotes() < 1:
            return 0
        
        self.member.asivotes_set.create(table=asi)

        return self.getFreeVotes()

    def unvote(self, asi):
        votes = self.member.asivotes_set.all().filter(table=asi)

        if len(votes) > 0:
            votes[0].delete()

    def numVotes(self, asi):
        return len(self.member.asivotes_set.all().filter(table=asi))

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
    
    def get(self):
        table_id = self.request.GET.get('table', '')
        self.table = helpers.get_asi(table_id, self.member.proj)
        func = self.request.GET.get('function', '')
        
        #supporter
        if func == 'supporter':
            return self.supporter()
        
        #editor
        if func == 'pad':
            return self.viewPad()
        
        #votes
        if func == 'votes':
            return self.getVotes()
        
        v = HTMLMember(self.member).getMaxVotes()

        #main page
        return render(self.request, 'topicauction/member_join_asi.html', {
            'project' : self.member.proj, 
            'member': self.member, 
            'table': self.table, 
            'votes':range(v) 
            })

    def post(self):
        table_id = self.request.POST.get('table', '')
        self.table = helpers.get_asi(table_id, self.member.proj)
        func = self.request.POST.get('function', '')

        if(func == "plus"):
            HTMLMember(self.member).vote(self.table)
        if(func == "minus"):
            HTMLMember(self.member).unvote(self.table)

        return self.getVotes();

    """
    Pad function, renders etherpad
    """
    def viewPad(self):
        pad = Pad(self.table.uuid, self.member.name)
        asis = self.table.sisign_set.all()
        return render(self.request, 'topicauction/pad.html', {'asi': HTMLAsi(self.table, 0), 
            "etherpad": pad, 
            "supporter": asis, 
            'member' : self.member 
            })

    def supporter(self):
        asis = self.table.sisign_set.all()
        return render(self.request, 'topicauction/supporter.html', {'asi': HTMLAsi(self.table, 0), "supporter": asis})

    def getVotes(self):
        hm = HTMLMember(self.member)
        v = hm.getFreeVotes()
        mtv = hm.numVotes(self.table)
        tv = len(self.table.asivotes_set.all())
        n = hm.getMaxVotes()
        data = {'member_votes_left':v, 'member_topic_voted': mtv, 'topic_voted':tv, 'max_votes': n}
        
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
        table_id = self.request.GET.get('table', '')
        page = int(self.request.GET.get('page', 1))
        
        #render tables overview
        step = Workflow.getStep(self.member.proj, 80, self.request)
        
        htables = HTMLAsi.getProjAsi(self.member.proj)
        
        #ceil (instead of math.ceil)
        pages = int(len(htables)/6) + 1
        if len(htables) % 6 > 0:
            pages = pages + 1
        
        v = HTMLMember(self.member).getMaxVotes()
        
        return render(self.request, 'topicauction/member_asi_overview.html', {'project' : self.member.proj, 
            'member': self.member, 
            'tables': htables,
            'tables': htables[(page-1)*6:page*6], 
            'pages': range(1, pages), 
            'page':page,
            'votes':range(v),
            'step': step})

#moderator pages
class ModeratorASIOverview(helpers.ModeratorRequest):
    def __init__(self, request, pid):
        helpers.ModeratorRequest.__init__(self,request, pid)

    def get(self):
        page = int(self.request.GET.get('page', 1))
        
        htables = HTMLAsi.getProjAsi(self.proj)
        
        #calculate paging ceil (instead of math.ceil)
        pages = int(len(htables)/6) + 1
        if len(htables) % 6 > 0:
            pages = pages + 1
        
        return render(self.request, 'topicauction/moderator_asi_overview.html', {'project' : self.proj, 
            'tables': htables[(page-1)*6:page*6], 
            'pages': range(1, pages), 
            'page':page
            })

class ModeratorScheduler(helpers.ModeratorRequest):
    def __init__(self, request, pid):
        helpers.ModeratorRequest.__init__(self,request, pid)
        #wf post request is handled by workflow itself
        self.step = Workflow.getStep(self.proj, 80, request)
    
    def post(self):
        return render(self.request, 'topicauction/moderator_scheduler.html', {'project' : self.proj, 'step': self.step })
    
    def get(self):
        function = self.request.GET.get('function', '')
    
        if function == 'asi':
            #ASI page requested
            m = ModeratorASIOverview(self.request, self.proj.id)
            return m.process()
        
        #supporter
        if function == 'supporter':
            m = ModeratorJoinASI(self.request, self.proj)
            return m.supporter()
        
        #editor
        if function == 'pad':
            m = ModeratorJoinASI(self.request, self.proj)
            return m.viewPad()
        
        #join
        if function == 'join':
            m = ModeratorJoinASI(self.request, self.proj)
            return m.joinAsi()
        
        #scheduling page requested
        return render(self.request, 'topicauction/moderator_scheduler.html', {'project' : self.proj, 'step': self.step })

class ModeratorJoinASI:
    def __init__(self, request, proj):
        self.request = request
        table_id = self.request.GET.get('table', '')
        self.table = Table.objects.get(pk=table_id)
        self.name = self.request.user.get_username
        self.proj = proj

    def supporter(self):
        asis = self.table.sisign_set.all()
        return render(self.request, 'topicauction/supporter.html', {"sign": asis})

    def viewPad(self):
        pad = Pad(self.table.uuid, self.name)
        pad.setReadOnly()
        asis = self.table.sisign_set.all()
        return render(self.request, 'topicauction/pad.html', {'table': self.table, "etherpad": pad, "sign": asis, 'project' : self.proj })
    
    def joinAsi(self):
        #main page
        jitsi = Jitsi(self.table.uuid, self.table.card.heading, self.name)
        return render(self.request, 'problemjostle/moderator_join_asi.html', {'project' : self.proj, 'table': self.table, 'jitsi': jitsi })
