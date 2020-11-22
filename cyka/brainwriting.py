from django.shortcuts import render, redirect
from .models import Member, Table, Card 
from . import helpers
from .workflow import Workflow
from .forms import CardForm

def getIndex(l, e):
    index = 0
    for a in l:
        if a == e:
            return index
        index = index + 1
    return None


class ModeratorScheduler(helpers.ModeratorRequest):
    def __init__(self, request, pid):
        helpers.ModeratorRequest.__init__(self,request, pid)
        #get step and save if changed, TODO refactor, ugly
        self.step = Workflow.getStep(self.proj, 40, request)
    
    def post(self):
        return self.getSi()
    
    def get(self):
        function = self.request.GET.get('function', '')

        return self.getSi()
    
    def getSi(self):
        #show only agreed
        cards = self.proj.card_set.all()
        
        return render(self.request, 'brainwriting/moderator_si_overview.html', {'project' : self.proj, 
            'cards': cards, 
            'step': self.step, 
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
            cards = self.member.card_set.all()
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

                return self.getOverviewMy(form)
        #return to overview
        return self.getOverviewMy()

    def get(self):
        card_id = self.request.GET.get('card', '')
        
        #render overview
        if card_id == '':
            if self.request.GET.get('cards', '') == 'all' or self.step.status == 'B':
                #show all cards
                return self.getOverviewAll()
            #show only cards of user
            return self.getOverviewMy()
        
        #render change card
        card = helpers.get_card(card_id, self.member)
        form = CardForm(initial={'heading': card.heading, 'desc' : card.desc, 'cardid': card.id })
        return self.getOverviewMy(form)

    def getOverviewAll(self):
        cards = self.member.proj.card_set.all()
    
        return render(self.request, 'brainwriting/member_si_overview.html', {
            'project' : self.member.proj, 
            'member': self.member, 
            'cards': cards, 
            'step': self.step,
            'all' : True
            })
    
    def getOverviewMy(self, form=CardForm()):
        cards = self.member.card_set.all()
    
        return render(self.request, 'brainwriting/member_si_overview.html', {
            'form' : form,
            'project' : self.member.proj, 
            'member': self.member, 
            'cards': cards, 
            'step': self.step,
            'all' : False
            })
