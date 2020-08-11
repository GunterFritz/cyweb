from django.shortcuts import render, redirect
from .forms import TableForm
from .models import Member, Table
from .config import Jitsi, Pad
from . import helpers
from .workflow import Workflow

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
        func = self.request.GET.get('function', '')
        
        if table_id != '':
            self.table = Table.objects.get(pk=table_id)
        if self.table == None:
            raise("No such table")
        
        #editor
        if func == 'pad':
            return self.viewPad()
        
        #edit name of table
        if func == 'edit':
            return self.viewEdit()
        
        #main page
        jitsi = Jitsi(self.table.uuid, self.table.name, self.member.name)
        return render(self.request, 'cyka/personal_join_table.html', {'project' : self.member.proj, 'member': self.member, 'table': self.table, 'jitsi': jitsi })

    """
    Pad function, renders etherpad
    """
    def viewPad(self):
        pad = Pad(self.table.uuid, self.member.name)
        return render(self.request, 'cyka/table_editor.html', {'table': self.table, "etherpad": pad})

    """
    renders edit table name
    """
    def viewEdit(self):
        form = TableForm(initial={'name': self.table.name, 'tableid': self.table.id })
        return render(self.request, 'cyka/edit_table.html', {'project' : self.member.proj, 'member': self.member, 'form': form, 'table': self.table})


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
        #render new page
        if table_id == 'new':
            form = TableForm()
            return render(self.request, 'cyka/add_table.html', {'project' : self.member.proj, 'member': self.member, 'form': form})
    
        #render tables overview
        step = Workflow.getStep(self.member.proj, 70, self.request)
        tables = self.member.proj.table_set.all()
        return render(self.request, 'cyka/personal_table.html', {'project' : self.member.proj, 'member': self.member, 'tables': tables, 'step': step})

