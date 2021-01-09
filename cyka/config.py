import requests
import json

jitsi = 'meet.cyiko.ch'
jitsi = 'meet.jit.si'
#jitsi = 'meet.cyiko.org'
etherpad = "http://localhost:9001"
jitsi_api = "https://meet.jit.si/external_api.js"
#jitsi_api = "https://meet.cyiko.org/external_api.js"

apikey='04960b8f0c68a38fafe985a7e9f64f0f4c385b7cef81ba587df607ec7d80a0dc'

class Jitsi:
    def __init__(self, room, subject, name):
        self.domain = jitsi
        self.room = room
        #self.room = "wasserfall"
        #self.room = "cyiko"
        self.subject = subject
        self.name = name
        self.api = jitsi_api

class Pad:
    def __init__(self, pad, user):
        self.origin = pad
        self.pad = pad
        self.domain = etherpad + '/p'
        self.name = "embed_readwrite" #for readonly mode set to embed_readonly
        self.user = user
        self.api_key = apikey
        self.timeout = 25.000
        self.readOnlyID = ''

    def setReadOnly(self):
        url = etherpad + '/api/1/getReadOnlyID?padID=' + self.pad + '&apikey=' + self.api_key
        self.name = "embed_readonly"
        
        try:
            r = requests.get(url, timeout=self.timeout)
            data = json.loads(json.dumps(r.json()))
            self.readOnlyID = data['data']['readOnlyID']
        except:
            self.readOnlyID = 'r.None'
        
        self.pad = self.readOnlyID


