from lib.structure import Structure2 as Structure
from django.shortcuts import render, redirect
from .models import Member, Table, Card, SIsign
from .config import Jitsi, Pad
from . import helpers
from .workflow import Workflow
from django.db import transaction

"""
File to render the problem jostle
Used html member:
    cyka/personal_join_table.html
    cyka/personal_table.html
    cyka/table_editor.html
    cyka/edit_table.html
    cyka/add_table.html
    cyka/table_added.html
    cyka/supporter.html
"""

#wrapper
class HTMLAsi:
    def __init__(self, table, num):
        self.table = table
        self.supporter = len(self.table.sisign_set.all())
        self.progress = 100
        self.max = num
        if self.supporter < num:
            self.progress = int(self.supporter*100/num)
    
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
        card_id = self.request.GET.get('si', '')
        func = self.request.GET.get('function', '')
        
        #supporter
        if func == 'supporter':
            return self.supporter()
        
        #editor
        if func == 'pad':
            return self.viewPad()
        
        #main page
        jitsi = Jitsi(self.table.uuid, self.table.card.heading, self.member.name)
        return render(self.request, 'problemjostle/member_join_asi.html', {'project' : self.member.proj, 'member': self.member, 'table': self.table, 'jitsi': jitsi })

    """
    Pad function, renders etherpad
    """
    def viewPad(self):
        pad = Pad(self.table.uuid, self.member.name)
        asis = self.table.sisign_set.all()
        return render(self.request, 'problemjostle/pad.html', {'table': self.table, "etherpad": pad, "sign": asis, 'member' : self.member })

    def supporter(self):
        asis = self.table.sisign_set.all()
        return render(self.request, 'problemjostle/supporter.html', {"sign": asis})


"""
renders the table step of problem jostle
the basic view shows all tables
GET: render page with all tables
GET: + table='new' -> render create page
POST: add table
"""
class ASIOverview(helpers.MemberRequest):
    def __init__(self, request, uuid):
        helpers.MemberRequest.__init__(self,request, uuid)

    def get(self):
        table_id = self.request.GET.get('table', '')
        page = int(self.request.GET.get('page', 1))
        
        #render new page, select an card to create an asi
        if table_id == 'new':
            cards = self.member.proj.card_set.all()
            page = int(self.request.GET.get('page', 1))
            #ceil (instead of math.ceil)
            pages = int(len(cards)/6) + 1
            if len(cards) % 6 > 0:
                pages = pages + 1
            return render(self.request, 'problemjostle/member_select_si.html', {'project' : self.member.proj, 
                'member': self.member, 
                'cards': cards[(page-1)*6:page*6], 
                'pages': range(1, pages), 
                'page':page})
    
        #render tables overview
        step = Workflow.getStep(self.member.proj, 80, self.request)
        
        htables = HTMLAsi.getProjAsi(self.member.proj)
        
        #ceil (instead of math.ceil)
        pages = int(len(htables)/6) + 1
        if len(htables) % 6 > 0:
            pages = pages + 1
        
        return render(self.request, 'problemjostle/member_asi_overview.html', {'project' : self.member.proj, 
            'member': self.member, 
            'tables': htables,
            'tables': htables[(page-1)*6:page*6], 
            'pages': range(1, pages), 
            'page':page,
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
        return render(self.request, 'problemjostle/supporter.html', {"sign": asis})

    def viewPad(self):
        pad = Pad(self.table.uuid, self.name)
        pad.setReadOnly()
        asis = self.table.sisign_set.all()
        return render(self.request, 'problemjostle/pad.html', {'table': self.table, "etherpad": pad, "sign": asis, 'project' : self.proj })
    
    def joinAsi(self):
        #main page
        jitsi = Jitsi(self.table.uuid, self.table.card.heading, self.name)
        return render(self.request, 'problemjostle/moderator_join_asi.html', {'project' : self.proj, 'table': self.table, 'jitsi': jitsi })
