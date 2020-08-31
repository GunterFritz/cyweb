jitsi = 'meet.cyiko.ch'
jitsi = 'meet.jit.si'
etherpad = "http://localhost:9001/p"
jitsi_api = "https://meet.jit.si/external_api.js"

class Jitsi:
    def __init__(self, room, subject, name):
        self.domain = jitsi
        self.room = room
        self.subject = subject
        self.name = name
        self.api = jitsi_api

class Pad:
    def __init__(self, pad, user):
        self.pad = pad
        self.domain = etherpad
        self.name = "embed_readwrite" #for readonly mode set to embed_readonly
        self.user = user

    def setReadOnly(self):
        self.name = "embed_readonly"
