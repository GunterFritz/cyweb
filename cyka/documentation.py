from django.shortcuts import render, redirect
from .models import Topic, Member, Table, Card 
from . import helpers
from . import config
from .forms import CardForm
from .htmlobjects import HTML_Si, HTMLAsi

#member pages
class MemberOverview(helpers.MemberRequest):
    def __init__(self, request, uuid):
        helpers.MemberRequest.__init__(self,request, pid)
    
    def post(self):
        return self.get()
    
    def get(self):
        #show only agreed
        if 'pad' == self.request.GET.get('func', ''):
            return self.pad()

        htables = HTMLAsi.get_proj_asi(self.proj)
        sis = HTML_Si.get_proj_si(self.proj)
        agenda = helpers.Agenda(self.proj).get_agenda()
       
        return render(self.request, 'documentation/member_documentation.html', {'project' : self.proj, 
            'tables': htables, 
            'sis': sis,
            'agenda': agenda,
            })

    def pad(self):
        topic_id = self.request.GET.get('topic', '')

        topic = Topic.objects.get(pk=topic_id)
        table = topic.asi
        
        pad = config.Pad(str(table.uuid), self.request.user.get_username)
        pad.setReadOnly()
        mem = topic.assignment_set.all().filter(atype = 'M')
        critics = topic.assignment_set.all().filter(atype = 'C')
        
        return render(self.request, 'documentation/member_documentation_pad.html', {'project' : self.proj, 
            'table': table, 
            "etherpad": pad, 
            "critics": critics, 
            "assign": mem 
            })
        
#moderator pages
class ModeratorOverview(helpers.ModeratorRequest):
    def __init__(self, request, pid):
        helpers.ModeratorRequest.__init__(self,request, pid)
    
    def post(self):
        return self.get()
    
    def get(self):
        #show topic
        if 'pad' == self.request.GET.get('func', ''):
            return self.pad()
        
        #show asi/ non asi
        if 'asi' == self.request.GET.get('func', ''):
            return self.asi()

        htables = HTMLAsi.get_proj_asi(self.proj)
        sis = HTML_Si.get_proj_si(self.proj)
        agenda = helpers.Agenda(self.proj).get_agenda()
       
        return render(self.request, 'documentation/documentation.html', {'project' : self.proj, 
            'tables': htables, 
            'sis': sis,
            'agenda': agenda,
            })

    def asi(self):
        table_id = self.request.GET.get('table', '')

        table = Table.objects.get(pk=table_id)
        
        pad = config.Pad(str(table.uuid), self.request.user.get_username)
        pad.setReadOnly()
        
        return render(self.request, 'documentation/documentation_pad.html', {'project' : self.proj, 
            'table': table, 
            "etherpad": pad, 
            "critics": [], 
            "assign": [] 
            })
        

    def pad(self):
        topic_id = self.request.GET.get('topic', '')

        topic = Topic.objects.get(pk=topic_id)
        table = topic.asi
        
        pad = config.Pad(str(table.uuid), self.request.user.get_username)
        pad.setReadOnly()
        mem = topic.assignment_set.all().filter(atype = 'M')
        critics = topic.assignment_set.all().filter(atype = 'C')
        
        return render(self.request, 'documentation/documentation_pad.html', {'project' : self.proj, 
            'table': table, 
            "etherpad": pad, 
            "critics": critics, 
            "assign": mem 
            })
        
