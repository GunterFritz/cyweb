from lib.structure import Structure2 as Structure
from django.shortcuts import render, redirect
from .forms import TableForm
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
    def getProjAsi(proj, agreed):
        tables = proj.table_set.all()
        n = Structure.factory(proj.ptype).getMinAgreedPersons()
        htables = []
        for t in tables:
            if agreed == "true":
                h = HTMLAsi(t,n)
                if h.progress == 100:
                    htables.append(h)
            else:
                htables.append(HTMLAsi(t,n))
        
        return htables
        

#Member pages

"""
class to render the Topic creation step

"""
class MemberView:
    def __init__(self, request, uuid):
        #TODO refactor: uuid as url param
        self.member = helpers.get_member_by_uuid(uuid)
        self.request = request

    def process(self):
        if self.request.method == 'GET':
            return self.get()
    
        if self.request.method == 'POST':
            return self.post()

        return None

class AgreedStatementImportance(MemberView):
    def __init__(self, request, uuid):
        MemberView.__init__(self,request, uuid)
        self.table = None
    
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
        
        #edit name of table
        if func == 'sign':
            return self.sign()
        
        #main page
        jitsi = Jitsi(self.table.uuid, self.table.card.heading, self.member.name)
        return render(self.request, 'cyka/personal_join_table.html', {'project' : self.member.proj, 'member': self.member, 'table': self.table, 'jitsi': jitsi })

    """
    Pad function, renders etherpad
    """
    def viewPad(self):
        pad = Pad(self.table.uuid, self.member.name)
        asis = self.table.sisign_set.all()
        return render(self.request, 'cyka/table_editor.html', {'table': self.table, "etherpad": pad, "sign": asis, 'member' : self.member })

    """
    renders edit table name
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
        return render(self.request, 'cyka/supporter.html', {"sign": asis})


    def post(self):
        table_id = self.request.POST.get('tableid', '')
        if table_id != '':
            self.table = Table.objects.get(pk=table_id)
        if self.table == None:
            raise("No such table")
        
        #new and save actions
        form = TableForm(self.request.POST)
        if form.is_valid():
            table = form.save(self.table)
            table.proj = self.member.proj
            table.save()
        else:
            #input fields not valid
            return render(self.request, 'cyka/edit_table.html', {'project' : self.member.proj, 'member': self.member, 'form': form, 'table': table})
        #saved, back to pad
        pad = Pad(self.table.uuid, self.member.name)
        return render(self.request, 'cyka/table_editor.html', {'table': self.table, "etherpad": pad})


"""
renders the table step of problem jostle
the basic view shows all tables
GET: render page with all tables
GET: + table='new' -> render create page
POST: add table
"""
class ASIOverview(MemberView):
    def __init__(self, request, uuid):
        MemberView.__init__(self,request, uuid)

    #table created 
    def post(self):
        form = TableForm(self.request.POST)
        if form.is_valid():
            table = form.save()
            table.proj = self.member.proj
            table.save()
        else:
            #input fields not valid
            return render(self.request, 'cyka/add_table.html', {'project' : self.member.proj, 'member': self.member, 'form': form})
        return render(self.request, 'cyka/table_added.html', {'project' : self.member.proj, 'member': self.member, 'table': table})
    
    
    def get(self):
        table_id = self.request.GET.get('table', '')
        page = int(self.request.GET.get('page', 1))
        #show only agreed
        agreed = self.request.GET.get('agreed', 'false')
        
        #render new page
        if table_id == 'new':
            cards = self.member.proj.card_set.all()
            page = int(self.request.GET.get('page', 1))
            #ceil (instead of math.ceil)
            pages = int(len(cards)/6) + 1
            if len(cards) % 6 > 0:
                pages = pages + 1
            #form = TableForm()
            return render(self.request, 'cyka/add_table.html', {'project' : self.member.proj, 
                'member': self.member, 
                #'form': form, 
                'cards': cards[(page-1)*6:page*6], 
                'pages': range(1, pages), 
                'page':page})
    
        #render tables overview
        step = Workflow.getStep(self.member.proj, 70, self.request)
        
        htables = HTMLAsi.getProjAsi(self.member.proj, agreed)
        
        #ceil (instead of math.ceil)
        pages = int(len(htables)/6) + 1
        if len(htables) % 6 > 0:
            pages = pages + 1
        
        return render(self.request, 'cyka/personal_table.html', {'project' : self.member.proj, 
            'member': self.member, 
            'tables': htables,
            'tables': htables[(page-1)*6:page*6], 
            'agreed': agreed,
            'pages': range(1, pages), 
            'page':page,
            'step': step})

#moderator pages
class ModeratorView:
    def __init__(self, request, pid):
        #TODO refactor: uuid as url param
        self.proj = helpers.get_project(request, pid)
        self.request = request

    def process(self):
        if self.request.method == 'GET':
            return self.get()
    
        if self.request.method == 'POST':
            return self.post()

        return None

class ModeratorASIOverview(MemberView):
    def __init__(self, request, pid):
        ModeratorView.__init__(self,request, pid)

    def get(self):
        #show only agreed
        agreed = self.request.GET.get('agreed', 'false')
        page = int(self.request.GET.get('page', 1))
        
        #render tables overview
        step = Workflow.getStep(self.proj, 70, self.request)
        
        htables = HTMLAsi.getProjAsi(self.proj, agreed)
        
        #calculate paging ceil (instead of math.ceil)
        pages = int(len(htables)/6) + 1
        if len(htables) % 6 > 0:
            pages = pages + 1
        
        return render(self.request, 'cyka/moderator_asi_overview.html', {'project' : self.proj, 
            'tables': htables,
            'tables': htables[(page-1)*6:page*6], 
            'agreed': agreed,
            'pages': range(1, pages), 
            'page':page,
            'step': step})
