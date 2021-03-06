from django.shortcuts import render, redirect
from .config import Jitsi, Pad
from . import helpers
from .workflow import Workflow

"""
File to render the start
"""

class ModeratorScheduler(helpers.ModeratorRequest):
    def __init__(self, request, pid):
        helpers.ModeratorRequest.__init__(self,request, pid)
        #wf post request is handled by workflow itself
        self.step = Workflow.getStep(self.proj, 30, request)
    
    def post(self):
        return render(self.request, 'start/moderator_scheduler.html', {'project' : self.proj, 'step': self.step })
    
    def get(self):
        #scheduling page requested
        return render(self.request, 'start/moderator_scheduler.html', {'project' : self.proj, 'step': self.step })

class MemberStart(helpers.MemberRequest):
    def __init__(self, request, uuid):
        helpers.MemberRequest.__init__(self,request, uuid)
        self.step = Workflow.getStep(self.member.proj, 30, request)
    
    def get(self):
        return render(self.request, 'start/member_start.html', {
            'project' : self.member.proj, 
            'member': self.member, 
            'step': self.step})
