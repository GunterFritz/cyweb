from django.shortcuts import render, redirect
from .models import Member, Table, Card 
from . import helpers
from .workflow import Workflow
from .forms import CardForm

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


class MemberBrainwriting(helpers.MemberRequest):
    def __init__(self, request, uuid):
        helpers.MemberRequest.__init__(self,request, uuid)
        self.step = Workflow.getStep(self.member.proj, 40, self.request)

    def post(self):    
        #card added, deleted or changed 
        card_id = self.request.POST.get('cardid', '')
        delete = self.request.POST.get('delete', 'false')
        card = None
        if card_id != '':
            card = helpers.get_card(card_id, self.member)
        #delete action
        if delete == 'true' and card != None:
            card.delete()
        #new and save actions
        else:
            form = CardForm(self.request.POST)
            if form.is_valid():
                card = form.save(card)
                card.proj = self.member.proj
                card.member = self.member
                card.save()
            else:
                #input fields not valid
                return render(self.request, 'brainwriting/member_si_edit.html', {'project' : self.member.proj, 'member': self.member, 'form': form})
        cards = self.member.card_set.all()
        #return to overview
        return render(self.request, 'brainwriting/member_si_overview.html', {'project' : self.member.proj, 'member': self.member, 'cards': cards, 'step': self.step})

    def get(self):
        card_id = self.request.GET.get('card', '')
        #render create form
        if card_id == 'new':
            form = CardForm()
            return render(self.request, 'brainwriting/member_si_edit.html', {'project' : self.member.proj, 'member': self.member, 'form': form})
        #render overview
        if card_id == '':
            cards = self.member.card_set.all()
    
            return render(self.request, 'brainwriting/member_si_overview.html', {'project' : self.member.proj, 'member': self.member, 'cards': cards, 'step': self.step})
        
        #render change card
        card = helpers.get_card(card_id, self.member)
        form = CardForm(initial={'heading': card.heading, 'desc' : card.desc, 'cardid': card.id })
        return render(self.request, 'brainwriting/member_si_edit.html', {'project' : self.member.proj, 'member': self.member, 'form': form})

