from .models import Project, WorkflowElement
from operator import attrgetter

workflow = [
    {
        'name' : 'Vorbereitung',
        'order': 1,
        'steps': [
        {
            'step' : 10,
            'short': 'Vorbesprechung',
            'desc' : 'Legen Sie gemeinsam mit dem Auftraggeber das Thema und die Teilnehmer fest', 
            'link' : 'cyka:project_details',
            'icon' : 'home',
            'todo' : 'Klären Sie gemeinsam mit dem Auftraggeber das Generalthema und formulieren Sie die Ausgangsfrage. Die Ausgangsfrage sollte in der Art formuliert sein: \"Was müssen wir tun um ... zu erreichen.\"'
        },
        {
            'step' : 20,
            'short': 'Teilnehmer',
            'desc' : 'Laden Sie die Teilnehmer ein', 
            'link' : 'cyka:project_team',
            'icon' : 'supervisor_account',
            'todo' : "Legen Sie die Teilnehmer des Workshops fest. Klären Sie, wer aufgrund seines Wissens oder Erfahrung zur Lösung der Ausgangsfrage beitragen kann oder aufgrund seiner Position oder Funktion die Umsetzung entscheidend ist."
        }
        ]
    },{
        'name' : 'Problem Jostle',
        'order': 2,
        'steps' : [
        {
            'step' : 30,
            'short': 'Begrüßung',
            'desc' : 'Begrüßen Sie die Teilnehmer, führen Sie in den Workshop ein und stellen Sie die Ausgangsfrage vor', 
            'link' : 'cyka:jostle_welcome',
            'icon' : 'mediation',
            'todo' : 'Begrüßen Sie die Teilnehmer, führen Sie in den Workshop ein und lassen Sie durch den Auftraggeber die Ausgangsfrage vorstellen' 
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
        
        self.elem = elem
        self.done = elem.done
        elem.step = self.step
        elem.save()

    def save(self):
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
    def get(proj):
        sections = []
        for d in workflow:
            sections.append(Section(d, proj))
        return sorted(sections, key=attrgetter('order'))

    @staticmethod
    def getStep(proj, num):
        steps = []
        for d in workflow:
            for st in d['steps']:
                if st['step'] == num:
                    return Step(st, proj)
        return None

