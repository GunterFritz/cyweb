from .models import Project, WorkflowElement
from .forms import WorkflowElementFormProgress, WorkflowElementForm
from operator import attrgetter

workflow = [
    {
        'name' : 'Vorbereitung',
        'order': 1,
        'member' : False,
        'steps': [
        {
            'step' : 10,
            'short': 'Vorbesprechung',
            'desc' : 'Legen Sie gemeinsam mit dem Auftraggeber das Thema und die Teilnehmer fest', 
            'link' : 'cyka:project_details',
            'memberlink' : '',
            'icon' : 'home',
            'todo' : 'Klären Sie gemeinsam mit dem Auftraggeber das Generalthema und formulieren Sie die Ausgangsfrage. Die Ausgangsfrage sollte in der Art formuliert sein: \"Was müssen wir tun um ... zu erreichen.\"',
            'formtype' : 'check'
        },
        {
            'step' : 20,
            'short': 'Teilnehmer',
            'desc' : 'Laden Sie die Teilnehmer ein', 
            'link' : 'cyka:project_team',
            'memberlink' : '',
            'icon' : 'supervisor_account',
            'todo' : 'Legen Sie die Teilnehmer des Workshops fest. Klären Sie, wer aufgrund seines Wissens oder Erfahrung zur Lösung der Ausgangsfrage beitragen kann oder aufgrund seiner Position oder Funktion die Umsetzung entscheidend ist. Sie können auch Gäste einladen. Ein Gast kann dem Plenum als Referent oder Zuhörer beitreten. Ein Gast kann nicht an Arbeitsgruppen teilnehmen.',
            'formtype' : 'check'
        }
        ]
    },{
        'name' : 'Problem Jostle',
        'order': 2,
        'member' : True,
        'steps' : [
        {
            'step' : 30,
            'short': 'Begrüßung',
            'desc' : 'Begrüßen Sie die Teilnehmer, führen Sie in den Workshop ein und stellen Sie die Ausgangsfrage vor', 
            'link' : 'cyka:jostle_welcome',
            'memberlink' : 'cyka:personal_plenum',
            'icon' : 'mediation',
            'todo' : 'Begrüßen Sie die Teilnehmer, führen Sie in den Workshop ein und lassen Sie durch den Auftraggeber die Ausgangsfrage vorstellen', 
            'formtype' : 'radio'
        },
        {
            'step' : 40,
            'short': 'Brainwriting',
            'desc' : 'Die Teilnehmer schreiben Ihre Gedanken zur Ausgangsfrage auf', 
            'link' : 'cyka:admin_brainwriting',
            'memberlink' : 'cyka:personal_card',
            'icon' : 'create',
            'todo' : 'Lassen Sie den Teilnehmern 5 - 15 Minuten Zeit, um ihre Gedanken zur Ausgangsfrage aufzuschreiben. Die Teilnehmer sehen nur ihre eigenen Karten.', 
            'formtype' : 'radio'
        },
        {
            'step' : 50,
            'short': 'Voting',
            'desc' : 'Die Teilnehmer können besonders wichtigen Gedanken zustimmen', 
            'link' : 'cyka:admin_votes',
            'memberlink' : 'cyka:personal_votes',
            'icon' : 'create',
            'todo' : 'Die Teilnehmer können nun alle Karten sehen. Lassen Sie den Teilnehmern 5 - 15 Minuten Zeit, um diese durchzusehen. Gedanken, die besonders wichtig sind können markiert weden.', 
            'formtype' : 'radio'
        },
        {
            'step' : 60,
            'short': 'Tagungscafe',
            'desc' : 'Die Teilnehmer tauschen sich in zufälligen Gruppen zur Ausgangsfrage aus', 
            'link' : 'cyka:jostle_welcome',
            'memberlink' : 'cyka:personal_workflow',
            'icon' : 'mediation',
            'todo' : 'Die Teilnehmer tauschen sich in zufälligen Gruppen zur Ausgangsfrage aus', 
            'formtype' : 'radio'
        }
        ]
    }
]


class Step:
    def __init__(self, args, proj):
        elem = proj.workflowelement_set.all().filter(step=args['step'])
        if len(elem) == 0:
            elem = proj.workflowelement_set.create()
        else:
            elem = elem[0]

        self.step = int(args['step'])
        self.desc = args['desc']
        self.short = args['short']
        self.link = args['link']
        self.icon = args['icon']
        self.todo = args['todo']
        self.memberlink = args['memberlink']
        self.formtype = args['formtype']
        self.form = None
        
        self.elem = elem
        self.done = elem.done
        self.status = elem.status
        elem.step = self.step
        elem.save()

    def save(self):
        if self.formtype == 'check':
            self.elem.done = self.done

        if self.formtype == 'radio':
            self.elem.status = self.status
            if self.status == 'B':
                self.elem.done = True
            else:
                self.elem.done = False
        self.elem.save()

class Section:
    def __init__(self, d, proj):
        self.name = d['name']
        self.order = d['order']
        
        steps = []
        for st in d['steps']:
            steps.append(Step(st, proj))
        self.steps = sorted(steps, key=lambda step: step.step)

class Workflow:
    @staticmethod
    def get(proj, admin = True):
        sections = []
        for d in workflow:
            if admin == True or d['member'] == True:
                sections.append(Section(d, proj))
        return sorted(sections, key=attrgetter('order'))

    @staticmethod
    def getStep(proj, num, request):
        step = None
        for d in workflow:
            for st in d['steps']:
                if st['step'] == num:
                    step = Step(st, proj)

        if step == None:
            return None
        
        step.form = None
        if request.method == 'POST':
            if 'step' in request.POST:
                if step.formtype == 'check':
                    step.form = WorkflowElementForm(request.POST)
                else:
                    step.form = WorkflowElementFormProgress(request.POST)
                if step.form.is_valid():
                    step.form.save(step)
                    step.save()
        if step.form == None:
            if step.formtype == 'check':
                step.form = WorkflowElementForm(initial={'done': step.done})
            else:
                step.form = WorkflowElementFormProgress(initial={'status': step.status})
        return step

