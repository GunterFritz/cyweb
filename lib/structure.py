from copy import deepcopy
from random import shuffle
from .algorithm import Person
from .algorithm import Topic
import sys
import operator
import numpy as np

class Edge:
    def __init__(self, name, index, color = None):
        self.name = name    #??
        self.index = index  #??
        self.struts = []    #array of connected struts
        self.color = color  #color
        self.topic = None   #topic
        #self.Topic = None

    """
    adds an Strut to that edge
    ---
    params
      strut: Strut that must be added
    """
    def addStrut(self, strut):
        self.struts.append(strut)
        strut.addEdge(self)

    """
    assigns a topic to that edge
    ---
    params
      Topic
    return
      last assigned Topic
    """
    def assignTopic(self, topic):
        retval = self.topic
        self.topic = topic
        return retval

    """
    assigns a list of persons to all connected struts
    ---
    params:
      person, Person[]: list of persons
    """
    def assignPersons(self, persons):
        for p in persons:
            for s in self.struts:
                if not s.empty and s.numPerson() == 0:
                    s.assignPerson(p)
                    break
                if s.empty:
                    print("DEBUG", s.getLeft().color, s.getRight().color)

    """
    counts number of connected persons
    ---
    params
      all_struts, Bool: if True returns all struts, otherwise only real persons
    ---
    return 
      number of persons
    """
    def getNumConnected(self, all_struts = False):
        if all_struts:
            return len(self.struts)
        retval = 0
        for s in self.struts:
            if not s.empty:
                retval = retval + 1
        return retval

    """
    finds a connection between two edges and returns the strut
    ---
    params rhs: Edge
    ---
    return
       Strut
    """
    def getConnectedStrut(self, rhs):
        for s in self.struts:
            if s in rhs.getStruts():
                return s
        raise Exception("Connection not found")

    """
    collects all assigned neigbhours
    ---
    return
      Edge[], Topic[]
    """
    def getNeighbours(self):
        topics = []
        edges = []
        for s in self.struts:
            n = s.getNeighbour(self)
            edges.append(n)
            if n.topic:
                topics.append(n.topic)
        return edges, topics

    """
    collects all assigned persons
    ---
    return
      Person[]
    """
    def getPersons(self):
        retval = []
        for s in self.struts:
            retval = retval + s.getPerson()
        return retval

    """
    searches a person and returns the strut
    ---
    params
      person 
    return: strut where person is assigned to
            NONE if not found
    """
    def assignTopicToPerson(self, topic, person):
        for s in self.struts:
            if person in s.getPerson():
                s.getNeighbour(self).topic = topic
                return
                    
        raise Exception("couldn't assign topic to person")

    """
    switches the topics, if a second edge is given, the persons are switch to
    """
    def switchAssignments(self, rhs, edge = None):
        if self == rhs:
            return
        topic = rhs.topic
        rhs.topic = self.topic
        self.topic = topic
        if edge:# and not edge.getConnectedStrut(self).isEmpty() and\
            #not edge.getConnectedStrut(rhs).isEmpty():
            edge.getConnectedStrut(self).switchPerson(edge.getConnectedStrut(rhs))



    """
    returns a list with all positions of its struts
    ---
    return
       [] (1,2)
    """
    def getPositions(self):
        pos = []
        pos = []
        for s in self.struts:
            pos.append(s.position)
        return pos

    """
    Topic getter
    """
    def getTopic(self):
        return self.topic

    """
    Strut getter
    """
    def getStruts(self):
        return self.struts

class Strut:
    def __init__(self, position):
        self.person = []
        self.empty = False  #True if person keeps None
        self.edge1 = None   #First edge/ topic
        self.edge2 = None   #second edge/ topic
        self.position = position   #position in geometry

    def debugName(self, topic = None):
        if topic and self.person:
            string = ""
            for p in self.person:
                string = string + ", Name: " + p.name + ", Rank(" + str(p.getRank(topic)) + ")"
            return "Empty: " + str(self.empty) + " " + str(self.edge1.index) + "," + str(self.edge2.index) + string
        return str(self.empty) + " " + str(self.edge1.index) + "," + str(self.edge2.index)

    """
    adds an Edge to that strut
    ---
    params
      edge: Edge that must be added
    """
    def addEdge(self, edge):
        if self.edge1 == None:
            self.edge1 = edge
            return True
        if self.edge2 == None:
            self.edge2 = edge
            return True
        return False
    
    def getPerson(self):
        return self.person

    def numPerson(self):
        return len(self.person)
   
    """
    switches the assigned persons
    """
    def switchPerson(self, rhs):
        person = self.person
        self.person = rhs.person
        rhs.person = person

    def getSatisfaction(self, person = None):
        #calculate sat for specific person
        if person:
            return person.satisfaction(self.edge1.getTopic(), self.edge2.getTopic())

        #nothing assigned
        if len(self.person) == 0:
            return 100

        #accumulate
        retval = 0
        for p in self.person:
            retval = retval + p.satisfaction(self.edge1.getTopic(), self.edge2.getTopic())
        return retval
    
    def switchIfBetter(self, rhs):
        for p in self.person:
            for p_r in rhs.person:
                current = self.getSatisfaction(p) + rhs.getSatisfaction(p_r)
                tmp = self.getSatisfaction(p_r) + rhs.getSatisfaction(p)
                
                if current > tmp:
                    self.person.remove(p)
                    self.person.append(p_r)
                    rhs.person.remove(p_r)
                    rhs.person.append(p)
        
    """
    each strut has two neighbours, returns that edge, that is not given
    ---
    params
      edge: start edge
    return
      edge: the neigbhour of edge
    """
    def getNeighbour(self, edge):
        if self.edge1 == edge:
            return self.edge2
        if self.edge2 == edge:
            return self.edge1
        
        raise Exception("couldn't find neighbour, edge not connected")

    def getLeftStrut(self, struts):
        for s in struts:
            if self.position[0] == s.position[1]:
                return s
        raise Exception("couldn't find left strut")
    
    def getRight(self):
        return self.edge2
    
    def getLeft(self):
        return self.edge1

    def assignPerson(self, p, second=False):
        if len(self.person) == 0 or second:
            self.person.append(p)
        elif not second:
            raise Exception("person already assigned to")
    
    """
    assigns the moset satisfied person to that strut
    ---
    params
      persons [] list of persons
    """
    def assignPersonFromList(self, persons):
        if self.edge1.getTopic() == None or\
           self.edge2.getTopic() == None:
            raise Exception("Cannnot close, edge without a topic")
        
        p, s = Person.getMostSatisfied(persons, self.edge1.getTopic(), self.edge2.getTopic())
        self.assignPerson(p)
        return p


    """
    searches an edge with topic and switches
    """
    def switchWithTopic(self, topic, edges, head):
        if self.topic == topic:
            return
        for e in edges:
            if e.topic == topic:
                self.switchAssignments(e, head)
                return
        raise Exception("cannot find topic to switch")

    """
    empty getter
    """
    def isEmpty(self):
        return self.empty

class Structure2:
    def __init__(self, optimal):
        self.numTopics = 0        
        self.numPersons = 0
        #the optimal number of Persons(struts) (Okta 12, Iso 30)
        self.optimalPersons = optimal
        self.type = ""
        self.struts = []
        self.positions = None
        self.colors = None
        #self.persons = None
        self.test = None
        self.opposites = None
        self.edges = []       #array of all topics
        self.persons = []      #array of all persons
        
        self.orig_persons = []
        self.orig_topics = []
    
    """
    creates an object by name or number of topics
    """
    def factory(t):
        if t == "O" or t == "OKTAEDER" or t == 6:
            return Oktaeder()
        if t == "I" or t == "IKOSAEDER" or t == 12:
            return Ikosaeder()

   
    def getMinPersons(self):
        return self.minPersons
    
    def getMaxPersons(self):
        return self.maxPersons

    def getNumTopics(self):
        return self.numTopics
    
    """
    initializes the edges with color and index
    
    params
    """
    def basic(self):
        #create topics with colors
        for c in self.colors:
            t = Edge("-", self.colors[c], c)
            self.edges.append(t)

    """
    the function splits the list z into all combinations of a subset
    with num elements of the list
    ---
    params
      num: (number) size of the subset
      z: list
    ---
    return
      list[] with all subsets
    """
    def split(self, num, z):
        inputlist = []
        retval = []
        self.split2(num, z, inputlist, retval)
    
        return retval
    
    def split2(self, num, z, inputlist, retval):
        if len(z) + len(inputlist) < num:
            return
        if len(inputlist) == num:
            retval.append(inputlist)
            return
    
        self.split2(num, z[1:], inputlist.copy(), retval)
        
        i2 = inputlist.copy()
        i2.append(z[0])
        self.split2(num, z[1:], i2, retval)

    """
    finds the best combination for a set
    ---
    params
       persons [], list of persons
    """
    def distribute(self, persons):
        possibilities = []
        #calculate all possible (sub)sets, possibilities is a list of subsets
        #each subset is a list of possitions
        for z in self.sets:
            possibilities = possibilities + self.split(len(persons), z)
        
        sat = 100
        pos = None
        for p in possibilities:
            #TODO: calculate satisfaction for each posibility
            struts = self.posToStrut(p)
            sat_t, pos_t = self.calculatePossibility(struts, persons)
            if sat_t < sat:
                sat = sat_t
                pos = pos_t

        for p in pos:
            p[0].assignPerson(p[1], True)


    """
    calculates the assignment for a possibility
    ---
    params
       struts [] list of strut
       persons [] list of persons
    return
       satisfaction, list of (strut, person)
    """
    def calculatePossibility(self,struts, persons):
        if len(struts) != len(persons):
            raise("Error: Number of persons does not match struts")
        _persons = persons.copy()
        retval = []
        #just add a person to each strut
        for s in struts:
            pers = None
            sat = 100
            for p in _persons:
                sp = s.getSatisfaction(p)
                if sp < sat:
                    sat = sp
                    pers = p
            _persons.remove(pers)
            retval.append([s,pers])

        #optimize
        for v1 in retval:
            for v2 in retval:
                if v1 == v2:
                    continue
                #switch
                if v1[0].getSatisfaction(v1[1]) + v2[0].getSatisfaction(v2[1]) > \
                   v1[0].getSatisfaction(v2[1]) + v2[0].getSatisfaction(v1[1]):
                       tmp = v2[1]
                       v2[1] = v1[1]
                       v1[1] = tmp
        
        #calculate sum
        sat = 0
        for v in retval:
            sat = sat + v[0].getSatisfaction(v[1])
        return sat, retval


    """
    transforms (or finds) a possibiliy into the corresponding struts
    ---
    params
       possibility [] list of positions (1,2)
    return
       Struts []
    """
    def posToStrut(self, possibility):
        retval = []
        for pos in possibility:
            for s in self.struts:
                if pos == s.position:
                    retval.append(s)
        
        if len(possibility) != len(retval):
            raise("Error, length missmatch")
        return retval

    def optimize(self):
        #if pers is None:
        #    pers = self.ring.pers + self.star.pers
        
        self.struts.sort(key=operator.methodcaller("getSatisfaction"), reverse=True)

        for s1 in self.struts:
            if s1.isEmpty():
                continue
            for s2 in self.struts:
                if s2.isEmpty():
                    continue
                if s1 == s2:
                    continue
                s1.switchIfBetter(s2)
    
    """
    creates the basic structure from configuration
    
    params
    """
    def create(self):
        #if less person than optimal
        num_empty = self.optimalPersons - self.numPersons
        empty = []

        if num_empty > 0:
            empty = self.sets[0][:num_empty]
        for pos in self.positions:
            strut = Strut(pos)
            self.struts.append(strut)
            self.edges[pos[0] - 1].addStrut(strut) #add left
            self.edges[pos[1] - 1].addStrut(strut) #add right
            #TODO when strut matches a set and not enough persons
            #keep it free
            if pos in empty:
                strut.empty = True

    """
    calculates current satisfaction for all assigned Persons
    """
    def getSatisfaction(self):
        sat = 0
        i = 0
        for s in self.struts:
            if s.numPerson() > 0:
                sat = sat + s.getSatisfaction()
                #print(s.person.name, s.getSatisfaction())
                i = i + s.numPerson()

        self.satisfaction = sat/i
        return self.satisfaction
    """
    reads the priority list from a two dimensional array
    each line is one Person

    params
    -------
    array: two dimensional array
        line: Person ID; topic one; topic 2; ...
    """
    def array_init(self, array):
        for line in array:
            p = Person(line[0])
            p.listinput(line[1:])
            self.orig_persons.append(p)
        
        for i in range(1, self.numTopics + 1):
            name = "T_" + str(i).zfill(2)
            p = Topic(name, i)
            self.orig_topics.append(p)

        self.numPersons = len(self.orig_persons)
        return None

    """
    creates topic list and persons random
    purpose is testing

    params
    -------
    num_pers: number of person 
    """
    def random_init(self, num_pers = 12):
        self.orig_persons = []
        self.orig_topics = []
        self.numPersons = num_pers
        for i in range(0, self.numPersons):
            name = "P_" + str(i).zfill(2)
            p = Person(name)
            p.random(self.numTopics)
            self.orig_persons.append(p)
        
        for i in range(1, self.numTopics + 1):
            name = "T_" + str(i).zfill(2)
            p = Topic(name, i)
            self.orig_topics.append(p)
    
    def file_init(self, filename):
        fobj = open(filename, "r")
        for line in fobj:
            p = Person(line.split(';')[0])
            p.listinput(line.split(';')[1:])
            self.orig_persons.append(p)
        
        for i in range(1, self.numTopics + 1):
            name = "T_" + str(i).zfill(2)
            p = Topic(name, i)
            self.orig_topics.append(p)

        self.numPersons = len(self.orig_persons)
        return None
    """
    prints the arrays of Person:
       name1; Rank; Rank; ...
       name2; Rank; Rank; ...
       ...
    ----
    params
        filename: name of file (if None-> stdout)
    """
    def print_out(self, filename = None):
        fobj = None
        if filename:
            fobj = open(filename, "w")
        for p in self.orig_persons:
            p.out(fobj)

    """
    creates the agenda
    [
    [[Topic 1],[Opposite]],
    [[Topic 2],[Opposite]],
    ...
    ]
    """
    def getAgenda(self):
        retval = []
        for t in self.opposites:
            print(t[0], "x", t[1])
            print(self.colors[t[0]]-1, "y", self.colors[t[1]]-1)
            print(self.edges[self.colors[t[0]]-1], "z", self.edges[self.colors[t[1]]-1])
            retval.append([self.edges[self.colors[t[0]]-1], self.edges[self.colors[t[1]]-1]])
        return retval

    def printAgenda(self):
        print("Stat:")
        print(self.count_popularity())
        agenda = self.getAgenda()
        for h in agenda:
            print("-----")
            print(h[0].color, h[0].topic.name if h[0].topic else None)
            #print left side
            for s in h[0].struts:
                print("  ", s.debugName(h[0].topic))
            print(h[1].color, h[1].topic.name if h[1].topic else None)
            #print opposite
            for s in h[1].struts:
                print("  ", s.debugName(h[1].topic))
        print("Satisfaction:", self.getSatisfaction())
    """
    creates it
    """
    def make(self):
        build_ring
    
    def build_ring2(self, topics, persons, edge):
        head = Topic.getLeastPopular(topics, persons)
        edge.assignTopic(head)
        topics.remove(head)
        
        struts = edge.getStruts()

        for s in struts:
            if not s.isEmpty():
                p = s.assignPersonFromList(persons)
                persons.remove(p)

    def build_ring(self, topics, persons, edge):
        #build star
        #select least popular topic as center and assign to edge
        head = Topic.getLeastPopular(topics, persons, 2)
        edge.assignTopic(head)
        topics.remove(head)
        
        #select persons who likes center topic most
        pers = head.nPersonsLikeTopic(persons, edge.getNumConnected())
        
        #assign persons to struts of edge
        edge.assignPersons(pers)
        for p in pers:
            persons.remove(p)

        #assign second topic to each person
        edge_persons = edge.getPersons()
        edge_persons.sort(key=operator.methodcaller("getRank", edge.getTopic()), reverse=True)
       
        for p in edge_persons:
            t = p.getMostBeautyfulTopic(topics)
            edge.assignTopicToPerson(t,p)
            #topic no longer selectable
            topics.remove(t)
        
        #build ring
        self.selectRingPersons(persons, edge, topics)

        return None

    """
    returns the start strut, the start point a strut with matches first set
    """
    def getStart(self, edges):
        start_strut = None
        struts = []
        for i in range(0, len(edges)):
            for j in range(i+1,len(edges)):
                for s in edges[i].getStruts():
                    if s not in edges[j].getStruts():
                        continue
                    if s.position in self.sets[0] and start_strut is None:
                        start_strut = s
                    if s.getRight().getTopic() == None:
                        start_strut = s
                    if s in edges[j].getStruts():
                        struts.append(s)
        return start_strut, struts

    def getNext(self, strut, edge, struts):
        for s in edge.getStruts():
            if s != strut:
                return s, s.getNeighbour(edge)
        raise Exception("Could not find next")

    """
    sorts a list of topics into a ring(4 or 5 topics) and build the struts
    ---
    params
      persons: array of unsigned persons
      edge: star topic (not part of ring, but each topic is connected to) 
    """
    def selectRingPersons(self, persons, edge, topics):
       
        #get basic geometry information(edges) and topics
        ring_edges, ring_topics = edge.getNeighbours()
        start, ring_struts = self.getStart(ring_edges)
        topic = Topic.getLeastPopular(ring_topics, persons)
        tmp = start.getLeftStrut(ring_struts)
        pers = None
        left = len(ring_topics)
        edge1 = start.getLeft()
        edge2 = None
        for e in ring_edges:
            if topic == e.getTopic():
                edge2 = e
        edge1.switchAssignments(edge2, edge)

        while True:
            #close strut (last strut)
            if left < 3 and not tmp.isEmpty():
                #if less than optimize number of persons, edge could be unsigned
                if tmp.getLeft().getTopic() == None:
                    topic = Topic.getLeastPopular(topics, persons, 2)
                    #pers = tmp.getRight().getTopic().nPersonsLikeTopic(persons, 1)[0]
                    #2Personen zur Auswahl!!! Richtung 6. wie kann das "richtige Topic" selectiert werden
                    #t = pers.getMostBeautyfulTopic(topics)
                    tmp.getLeft().assignTopic(topic)
                    #tmp.assignPerson(pers)
                    #topic no longer selectable
                    topics.remove(topic)
                    #persons.remove(pers)
                #else:
                p = tmp.assignPersonFromList(persons)
                persons.remove(p)
            elif not tmp.isEmpty():

                ring_topics.remove(topic)

                pers = topic.nPersonsLikeTopic(persons, 1)[0]
                persons.remove(pers)
                tmp.assignPerson(pers)
                topic = pers.getMostBeautyfulTopic(ring_topics)

                #switch topics from edge to edge
                #alternative edge.switchWithTopic(topic, ring_edges, edge)
                edge1 = tmp.getLeft()
                edge2 = None
                for e in ring_edges:
                    if topic == e.getTopic():
                        edge2 = e

                #check if edge is correct, should not happen
                if edge2 == None:
                    raise Exception("Edge is empty")
                if edge1.index != tmp.position[0]:
                    raise Exception("edge does not match empty")
                
                edge1.switchAssignments(edge2, edge)
            
            left = left - 1
            if tmp == start:
                return None #break
            tmp = tmp.getLeftStrut(ring_struts)

        #TODO check if correct -> better do not use least popular
        #start with least popular topic
        least_pop = Topic.getLeastPopular(ring_topics, persons)
        if start.isEmpty():
            pers = least_pop.nPersonsLikeTopic(_persons, 1)
            end = pers[0].getMostBeautyfulTopic(_topics)
        else:
            pers = lp.nPersonsLikeTopic(_persons, 2)
            start.assignPerson(pers[0])
            persons.remove(pers)
            start.edge1.switchWithTopic(lp, ring_edges)
            next_edge = start.getNeighbour(edge1)

        tmp = None
        while tmp != start:
            a = None


        topics.remove(lp)
        #HOWTO SELECT RING
        #TODO ONE Person
        #optimization, add two person two least pop
        #process first person
        end = pers[0].getMostBeautyfulTopic(_topics)
        retval.append((pers[0],lp,end))
        _topics.remove(end)
        _persons.remove(pers[0])
        #process second person
        tmp = pers[1].getMostBeautyfulTopic(_topics)
        retval.append((pers[1],lp,tmp))
        _topics.remove(tmp)
        _persons.remove(pers[1])
            
        #process further ring
        while len(_topics) and len(_persons) > 0:
            #select persons for topic
            p = tmp.nPersonsLikeTopic(_persons, 1)[0]
            _persons.remove(p)
            tmp_next = p.getMostBeautyfulTopic(_topics)
            retval.append((p,tmp,tmp_next))
            tmp = tmp_next
            _topics.remove(tmp)

        #close last connection
        if close:
            p, s = Person.getMostSatisfied(_persons, end, tmp)
            retval.append((p,tmp,end))

        return retval
    
    """
    creates a statistic, how many people votes for topic
    ---
    return 
      [] [Topic, number of p, number of p, ...
         [Topic, number of p, number of p, ...
    """
    
    def count_popularity(self):
        #array
        count = np.zeros((self.numTopics, self.numTopics + 1), int)
        row = -1
        for t in self.orig_topics:
            #write index into first column
            row = row + 1
            count[row][0] = t.index
            for p in self.orig_persons:
                #iterate through the prioritylist of each person
                #and increment the topic at position of priority 
                for pindex in range(len(p.priorityList)):
                    if p.priorityList[pindex] == t.index:
                        count[row][pindex+1] = count[row][pindex+1] + 1
                        break
        return count
    

class Oktaeder(Structure2):
    def __init__(self, persons = 12):
        Structure2.__init__(self, persons)
        self.numTopics = 6
        self.minPersons = 9 
        self.maxPersons = 15
        self.optimalPersons = 12
        #self.numPersons = persons
        #self.topics = None
        #self.persons = None
        self.type = "Oktaeder"
        self.colors = {"white" : 1, "green" : 2, "blue" : 3, "yellow" : 4, "red" : 5, "black" : 6}
        self.positions = [(1,2),(1,3),(1,4),(1,5),(2,3),(3,4),(4,5),(5,2),(2,6),(3,6),(4,6),(5,6)]
        self.opposites ={ ("white", "black") , ("green", "yellow"), ("blue", "red")}
        self.sets = [[(1,2),(3,4),(5,6)],[(1,2),(4,5),(3,6)],
                        [(1,3),(5,2),(4,6)],[(1,3),(4,5),(2,6)]]
        #parts (1,2), (3,4), (5,6)
        #             (4,5), (3,6)
        #      (1,3), (4,5), (2,6)
        #             (2,5), (4,6)
        #      (1,4), (2,5), (3,6)
        #             (2,3), (5,6)
        #      (1,5), (2,3), (4,6)
        #             (3,4), (2,6)
        
        #opposites: 1-6, 2-4, 3-5

    def build(self):
        self.basic()
        self.create()
        #do not change original
        _topics = self.orig_topics[:]
        _persons = self.orig_persons[:]
        self.build_ring(_topics, _persons, self.edges[0])
        self.build_ring2(_topics, _persons, self.edges[5])
        self.optimize()

        print("Person left:", len(_persons))
        if len(_persons) > 0:
            self.distribute(_persons)
        exit
        
        #self.optimize()
        #self.optimize()

        #self.build_ring(_topics, _persons, self.edges[0].opposite())
        #close()

