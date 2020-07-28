#TODO refactor
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
            'icon' : 'personal_video',
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
            'icon' : 'thumb_up',
            'todo' : 'Die Teilnehmer können nun alle Karten sehen. Lassen Sie den Teilnehmern 5 - 15 Minuten Zeit, um diese durchzusehen. Gedanken, die besonders wichtig sind können markiert weden.', 
            'formtype' : 'radio'
        },
        {
            'step' : 60,
            'short': 'Tagungscafe',
            'desc' : 'Die Teilnehmer tauschen sich in zufälligen Gruppen zur Ausgangsfrage aus', 
            'link' : 'cyka:randsession',
            'memberlink' : 'cyka:personal_workflow',
            'icon' : 'free_breakfast',
            'todo' : 'Die Teilnehmer tauschen sich in zufälligen Gruppen zur Ausgangsfrage aus', 
            'formtype' : 'radio'
        },
        {
            'step' : 70,
            'short': 'Themenvorschläge',
            'desc' : 'Die Teilnehmer erarbeiten selbständig Themenvorschläge', 
            'link' : 'cyka:personal_workflow',
            'memberlink' : 'cyka:personal_table',
            'icon' : 'explore',
            'todo' : 'Die Teilnehmer erarbeiten selbständig Themenvorschläge', 
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
        self.before = None
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

    def toggleState(self):
        self.elem.done = not self.elem.done
        self.done = self.elem.done

        if self.elem.status == 'S':
            self.elem.status = 'B'
        else:
            self.elem.status = 'S'
        self.status = self.elem.status
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
    """
    get a sorted list with all steps
    """
    @staticmethod
    def get(proj, admin = True):
        sections = []
        for d in workflow:
            if admin == True or d['member'] == True:
                sections.append(Section(d, proj))
        return sorted(sections, key=attrgetter('order'))

    """
    returns a single step
    """
    @staticmethod
    def getStep(proj, num, request):
        step = None
        step_before = None
        for d in workflow:
            for st in d['steps']:
                if st['step'] == num:
                    step = Step(st, proj)
                elif st['step'] < num:
                    if step_before == None:
                        step_before = Step(st, proj)
                    elif step_before.step < st['step']: 
                        step_before = Step(st, proj)

        if step == None:
            return None

        if step_before != None:
            step.before = step_before
        
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

    @staticmethod
    def getActive():
        return None

