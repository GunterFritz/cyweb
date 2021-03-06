from lib.structure import Structure2 as Structure
from django.shortcuts import render, redirect
from .models import Member, Table, Card, SIsign
from .config import Jitsi, Pad
from . import helpers
from .workflow import Workflow
from .htmlobjects import HTML_Si, HTMLAsi
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

#Member pages

"""
class to render the Topic creation step

"""
class AgreedStatementImportance(helpers.MemberRequest):
    def __init__(self, request, uuid):
        helpers.MemberRequest.__init__(self,request, uuid)
        self.table = None
        self.step = Workflow.getStep(self.member.proj, 70, self.request)
    
    def get(self):
        table_id = self.request.GET.get('table', '')
        card_id = self.request.GET.get('si', '')
        func = self.request.GET.get('function', '')
        
        #get table from card or create if not assigned
        if card_id != '':
            c = Card.objects.get(pk=card_id)
            #check permissions
            if c.proj != self.member.proj:
                raise("No such table")

            with transaction.atomic():
                tables = c.table_set.all()
                if len(tables) == 0:
                    self.table = Table()
                    self.table.proj = c.proj
                    self.table.card = c
                    self.table.save()
                else:
                    self.table = tables[0]

        if self.table == None and table_id != '':
            self.table = Table.objects.get(pk=table_id)
        if self.table == None:
            raise("No such table")
        
        #supporter
        if func == 'supporter':
            return self.supporter()
        
        #editor
        if func == 'pad':
            return self.viewPad()
        
        #sign/ unsign an ASI
        if func == 'sign':
            return self.sign()
        
        #main page
        jitsi = Jitsi(self.table.uuid, self.table.card.heading, self.member.name)
        return render(self.request, 'problemjostle/member_join_asi.html', {'project' : self.member.proj, 
            'member': self.member, 
            'table': self.table, 
            'jitsi': jitsi, 
            'step': self.step })

    """
    Pad function, renders etherpad
    """
    def viewPad(self):
        pad = Pad(str(self.table.uuid), self.member.name)
        if self.step.done:
            pad.setReadOnly()
        asis = self.table.sisign_set.all()
        return render(self.request, 'problemjostle/pad.html', {'table': self.table, "etherpad": pad, "sign": asis, 'member' : self.member })

    """
    function to sign/ support or unsign an asi
    """
    def sign(self):
        asis = self.table.sisign_set.all().filter(member=self.member)
        #sign
        if len(asis) == 0:
            sign = SIsign()
            sign.member = self.member
            sign.table = self.table
            sign.save()
        #unsign
        else:
            asis[0].delete()

        return self.supporter()
    
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
        #show only agreed
        agreed = self.request.GET.get('agreed', 'false')
        
        step = Workflow.getStep(self.member.proj, 70, self.request)
        
        #render tables overview
        htables = HTMLAsi.get_proj_asi(self.member.proj, agreed)
        sis = HTML_Si.get_proj_si(self.member.proj)
        
        return render(self.request, 'problemjostle/member_asi_overview.html', {'project' : self.member.proj, 
            'member': self.member, 
            'tables': htables,
            'sis': sis,
            'agreed': agreed,
            'step': step})

#moderator pages
class ModeratorASIOverview(helpers.ModeratorRequest):
    def __init__(self, request, pid):
        helpers.ModeratorRequest.__init__(self,request, pid)
        self.step = Workflow.getStep(self.proj, 70, self.request)
    
    def post(self):
        return self.get()
    
    def get(self):
        #show only agreed
        agreed = self.request.GET.get('agreed', 'false')
       
        htables = HTMLAsi.get_proj_asi(self.proj, agreed)
        sis = HTML_Si.get_proj_si(self.proj)
        
        return render(self.request, 'problemjostle/moderator_asi_overview.html', {'project' : self.proj, 
            'tables': htables, 
            'agreed': agreed,
            'sis': sis,
            'step': self.step
            })

class ModeratorScheduler(helpers.ModeratorRequest):
    def __init__(self, request, pid):
        helpers.ModeratorRequest.__init__(self,request, pid)
        #wf post request is handled by workflow itself
        self.step = Workflow.getStep(self.proj, 70, request)
    
    def post(self):
        m = ModeratorASIOverview(self.request, self.proj.id)
        return m.process()
    
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
            return m.joinAsi(self.step)
            
        m = ModeratorASIOverview(self.request, self.proj.id)
        return m.process()
        
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
        pad = Pad(str(self.table.uuid), self.name)
        pad.setReadOnly()
        asis = self.table.sisign_set.all()
        return render(self.request, 'problemjostle/pad.html', {'table': self.table, "etherpad": pad, "sign": asis, 'project' : self.proj })
    
    def joinAsi(self, step):
        #main page
        step = Workflow.getStep(self.proj, 70, self.request)
        
        jitsi = Jitsi(self.table.uuid, self.table.card.heading, self.name)
        return render(self.request, 'problemjostle/moderator_join_asi.html', {
            'project' : self.proj, 
            'table': self.table, 
            'jitsi': jitsi, 
            'step': step 
            })
