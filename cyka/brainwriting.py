from lib.structure import Structure2 as Structure
from django.shortcuts import render, redirect
from .models import Member, Table, Card, SIsign
from .config import Jitsi, Pad
from . import helpers
from .workflow import Workflow

class ModeratorScheduler(helpers.ModeratorRequest):
    def __init__(self, request, pid):
        helpers.ModeratorRequest.__init__(self,request, pid)
        self.step = Workflow.getStep(self.proj, 40, request)
    
    def post(self):
        return render(self.request, 'brainwriting/moderator_scheduler.html', {'project' : self.proj, 'step': self.step })
    
    def get(self):
        function = self.request.GET.get('function', '')

        if function == 'si':
            return self.getSi()
    
        #scheduling page requested
        return render(self.request, 'brainwriting/moderator_scheduler.html', {'project' : self.proj, 'step': self.step })
    
    def getSi(self):
        #show only agreed
        page = int(self.request.GET.get('page', 1))
        
        cards = self.proj.card_set.all()
        
        #calculate paging ceil (instead of math.ceil)
        pages = int(len(cards)/6) + 1
        if len(cards) % 6 > 0:
            pages = pages + 1
        
        return render(self.request, 'brainwriting/moderator_si_overview.html', {'project' : self.proj, 
            'cards': cards[(page-1)*6:page*6], 
            'pages': range(1, pages), 
            'page':page
            })


