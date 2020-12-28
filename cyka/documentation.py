from django.shortcuts import render, redirect
from .models import Member, Table, Card 
from . import helpers
from .forms import CardForm
from .htmlobjects import HTML_Si, HTMLAsi

#moderator pages
class ModeratorOverview(helpers.ModeratorRequest):
    def __init__(self, request, pid):
        helpers.ModeratorRequest.__init__(self,request, pid)
    
    def post(self):
        return self.get()
    
    def get(self):
        #show only agreed
        htables = HTMLAsi.get_proj_asi(self.proj)
        sis = HTML_Si.get_proj_si(self.proj)
        agenda = helpers.Agenda(self.proj).get_agenda()
       
        return render(self.request, 'cyka/documentation.html', {'project' : self.proj, 
            'tables': htables, 
            'sis': sis,
            'agenda': agenda,
            })

