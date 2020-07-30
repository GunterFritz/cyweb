from django import forms
from django.forms import ModelForm
from .models import Project, Topic, Member, Card, Table
from material import Layout, Row, Column, Fieldset, Span2, Span3, Span5, Span6, Span10

#class ProjectForm(ModelForm):
#    class Meta:
#        model = Project
#        fields = ('name', 'question', 'ptype')

class ProjectForm(forms.Form):
    name = forms.CharField(label='Name')
    question = forms.CharField(label='Ausgangsfrage', max_length=500, widget=forms.Textarea(attrs={"style": "resize: none"}))
    ptype = forms.ChoiceField(choices=((None, ''), ('O', '9-15 Teilnehmer'), ('C', '16-24 Teilnehmer'), ('I', '25-36 Teilnehmer')), label='Gruppengröße')

    def save(self, prj = None):
        if prj == None:
            prj = Project()
        prj.name = self.cleaned_data['name']
        prj.question = self.cleaned_data['question']
        prj.ptype = self.cleaned_data['ptype']

        return prj


class TopicForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['desc'].required = False
        
    class Meta:
        model = Topic
        fields = ('name', 'desc',)

class TableForm(forms.Form):
    name = forms.CharField(label="Themenvorschlag")

    def save(self, table = None):
        if table == None:
            table = Table()
        table.name = self.cleaned_data['name']

        return table

class MemberForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    mtype = forms.ChoiceField(choices=(('M', 'Teilnehmer'), ('G', 'Gast')))

    def save(self, member = None):
        if member == None:
            member = Member()
        member.name = self.cleaned_data['name']
        member.email = self.cleaned_data['email']
        member.mtype = self.cleaned_data['mtype']

        return member

class WorkflowElementFormProgress(forms.Form):
    status = forms.ChoiceField(choices=(('O', 'Offen'), ('S', 'Starten'), ('B', 'Beendet')), label='Fortschritt', widget=forms.RadioSelect)

    def save(self, wf):
        wf.status = self.cleaned_data['status']
        return wf

class WorkflowElementForm(forms.Form):
    done = forms.BooleanField(label='erledigt', required=False)

    def save(self, wf):
        wf.done = self.cleaned_data['done']
        return wf

class MemberOkForm(ModelForm):
    class Meta:
        model = Member
        fields = ('status',)

class CardForm(forms.Form):
    heading = forms.CharField(label='Stichwort', max_length=60, widget=forms.Textarea(attrs={"style": "resize: none"}))
    desc = forms.CharField(label='Beschreibung', max_length=200, widget=forms.Textarea(attrs={"style": "resize: none", "class": "active"}))
    cardid = forms.CharField(widget=forms.HiddenInput(), required=False)
    delete = forms.CharField(widget=forms.HiddenInput(), required=False)

    def save(self, card = None):
        if card == None:
            card = Card()
        card.heading = self.cleaned_data['heading']
        card.desc = self.cleaned_data['desc']

        return card

