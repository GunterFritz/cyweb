jitsi = 'meet.cyiko.ch'
etherpad = "http://localhost:9001/p"

class Jitsi:
    def __init__(self, room, subject, name):
        self.domain = jitsi
        self.room = room
        self.subject = subject
        self.name = name

class Pad:
    def __init__(self, pad, user):
        self.pad = pad
        self.domain = etherpad
        self.name = "embed_readwrite" #for readonly mode set to embed_readonly
        self.user = user

    def setReadOnly(self):
        self.name = "embed_readonly"
