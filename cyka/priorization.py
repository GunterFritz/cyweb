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

    def get(self):
        func = self.request.GET.get('function', '')
        
        #votes
        if func == 'priority_list':
            return self.renderPriority()
        
        return self.renderPriority()
    
    def renderPriority(self):
        html_mem = HTMLMember(self.member)
        prio = html_mem.get_priority_list()
        
        return render(self.request, 'priorization/member_priority_list.html', {
            'project' : self.member.proj, 
            'member': self.member, 
            'priority_list': prio
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
            return self.renderMember()
        
        #scheduling page requested
        return render(self.request, 'priorization/moderator_scheduler.html', {
            'project' : self.proj,
            'step': self.step
            })

    def renderMember(self):
        member = self.proj.member_set.all().filter(mtype='M')
        
        return render(self.request, 'priorization/moderator_member_overview.html', {
            'project' : self.proj,
            'member' : member,
            'step': self.step
            })
