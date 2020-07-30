jitsi = 'meet.cyiko.org'
etherpad = "http://localhost:9001/p"

class Jitsi:
    def __init__(self, room, subject, name):
        self.domain = jitsi
        self.room = room
        self.subject = subject
        self.name = name

class Pad:
    def __init__(self, pad):
        self.pad = pad
        self.domain = etherpad
        self.name = "embed_readwrite" #for readonly mode set to embed_readonly
