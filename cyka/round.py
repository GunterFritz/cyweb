from lib.structure import Structure2 as Structure
from django.shortcuts import render, redirect
from .models import Member, Table, Topic, Card, SIsign
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
        n = Structure.factory(proj.ptype).getMinAgreedPersons(len(proj.member_set.all().filter(mtype='M')))
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
class MemberJoinTopic(helpers.MemberRequest):
    def __init__(self, request, uuid):
        helpers.MemberRequest.__init__(self,request, uuid)
        topic_id = self.request.GET.get('topic', '')
        self.topic = Topic.objects.get(pk=topic_id)
        self.table = self.topic.asi
        self.name = self.request.user.get_username
    
    def get(self):
        func = self.request.GET.get('function', '')
        
        if self.table == None:
            raise("No such table")
        
        #editor
        if func == 'pad':
            return self.viewPad()
        
        #if self.step.done: 
        #    return render(self.request, 'problemjostle/member_join_asi_finished.html', {'project' : self.member.proj, 'member': self.member, 'table': self.table })
        
        #main page
        jitsi = Jitsi(self.table.uuid, self.table.card.heading, self.member.name)
        return render(self.request, 'round/member_join_table.html', {'project' : self.member.proj, 'member': self.member, 'topic': self.topic, 'jitsi': jitsi })

    """
    Pad function, renders etherpad
    """
    def viewPad(self):
        pad = Pad(str(self.table.uuid), self.member.name)
        pad.setReadOnly()
        mem = self.topic.assignment_set.all().filter(atype = 'M')
        critics = self.topic.assignment_set.all().filter(atype = 'C')
        return render(self.request, 'round/pad.html', {
            'table': self.table, 
            "etherpad": pad, 
            "critics": critics, 
            "assign": mem 
            })

class ModeratorJoinTopic(helpers.ModeratorRequest):
    def __init__(self, request, pid):
        helpers.ModeratorRequest.__init__(self,request, pid)
        topic_id = self.request.GET.get('topic', '')
        self.topic = Topic.objects.get(pk=topic_id)
        self.table = self.topic.asi
        self.name = self.request.user.get_username

    def get(self):
        func = self.request.GET.get('function', '')
        #editor
        if func == 'pad':
            return self.viewPad()
        
        #join
        if func == 'join':
            return self.joinAsi()
        
        return self.joinAsi()
    
    def viewPad(self):
        pad = Pad(str(self.table.uuid), self.name)
        pad.setReadOnly()
        mem = self.topic.assignment_set.all().filter(atype = 'M')
        critics = self.topic.assignment_set.all().filter(atype = 'C')
        return render(self.request, 'round/pad.html', {'table': self.table, "etherpad": pad, "assign": mem, "critics": critics })
    
    def joinAsi(self):
        #main page
        jitsi = Jitsi(self.table.uuid, self.table.card.heading, self.name)
        return render(self.request, 'round/moderator_join_table.html', {
            'project' : self.proj, 
            'topic': self.topic, 
            'table': self.table, 
            'jitsi': jitsi 
            })
