import json
from lib.structure import Structure2 as Structure
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Member, Topic, Table, Card, SIsign
from .config import Jitsi, Pad
from . import helpers
from .workflow import Workflow
from .htmlobjects import HTMLMember
from django.db import transaction
from django.utils.safestring import SafeString

#Member pages

"""
renders all asi for that can be voted
the basic view shows all tables
GET: render page with all tables
"""
class Member(helpers.MemberRequest):
    def __init__(self, request, uuid):
        helpers.MemberRequest.__init__(self,request, uuid)

    def post(self):
        func = self.request.POST.get('function', '')

        #save order
        if func == 'push_order':
            return self.pushOrder()

        #set status to false, so that sorting is possible
        if func == 'reset':
            self.member.status = False
            self.member.save()
        
        
        return self.renderPriority()

    """
    saves the priorization from user
    """
    def pushOrder(self):
        data = self.request.POST.get('order', '')
    
        priority_list = self.member.priority_set.all()
       
        for p in priority_list:
            for u in json.loads(data):
                if p.topic.number == u['number']:
                    p.priority =u['order']
                    p.save()

        self.member.status = True
        self.member.save()
            #print(p.topic.name, p.priority)

        return self.renderPriority()
    
    def get(self):
        func = self.request.GET.get('function', '')
        
        #votes
        if func == 'priority_list':
            return self.renderPriority()
        
        #votes
        if func == 'agenda':
            return self.renderAgenda()
        
        return self.renderPriority()
    
    def renderPriority(self):
        html_mem = HTMLMember(self.member)
        prio = html_mem.get_priority_list()
        
        return render(self.request, 'priorization/member_priority_list.html', {
            'project' : self.member.proj, 
            'member': self.member, 
            'priority_list': prio
            })
    
    def renderAgenda(self):
        if not self.member.proj.hasagenda:
            return None

        agenda = helpers.Agenda(self.member.proj)
        
        return render(self.request, 'priorization/member_agenda.html', {
            'project' : self.member.proj,
            'member': self.member, 
            'agenda' : agenda.get_agenda()
            })




#moderator pages
class Moderator(helpers.ModeratorRequest):
    def __init__(self, request, pid):
        helpers.ModeratorRequest.__init__(self,request, pid)
        #wf post request is handled by workflow itself
        self.step = Workflow.getStep(self.proj, 90, request)
    
    def post(self):
        return render(self.request, 'priorization/moderator_scheduler.html', {'project' : self.proj, 'step': self.step })
    
    def get(self):
        function = self.request.GET.get('function', '')
    
        #show votes of members
        if function == 'member':
            return self.renderMemberOverview()
        
        #show the agenda (assigned persons to topics)
        if function == 'agenda':
            return self.showAgenda()
        
        #assign topics to edges and persons to struts
        if function == 'assign':
            self.createAgenda()
            return self.showAgenda()
        
        if function == 'resolve':
            agenda = helpers.Agenda(self.proj)
            agenda.resolve_agenda()
            return self.renderMemberOverview()
        
        #show details of an specific members
        if function == 'details':
            return self.renderMemberDetails()
        
        #scheduling page requested
        return render(self.request, 'priorization/moderator_scheduler.html', {
            'project' : self.proj,
            'step': self.step
            })
    """
    assigns each topic to an edge and each person to a strut
    """
    def createAgenda(self):
        agenda = helpers.Agenda(self.proj)
        agenda.create_agenda()

    def renderMemberDetails(self):
        member_id = self.request.GET.get('member', '')
        member = helpers.get_member(self.request, member_id)
        
        return render(self.request, 'priorization/moderator_member_detail.html', {
            'project' : self.proj,
            'member': member
            })
    
    def renderMemberOverview(self):
        member = self.proj.member_set.all().filter(mtype='M')
        
        return render(self.request, 'priorization/moderator_member_overview.html', {
            'project' : self.proj,
            'member' : member,
            'step': self.step
            })
    
    def showAgenda(self):
        agenda = helpers.Agenda(self.proj)
        
        return render(self.request, 'priorization/moderator_agenda.html', {
            'project' : self.proj,
            'agenda' : agenda.get_agenda()
            })

