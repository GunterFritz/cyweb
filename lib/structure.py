from copy import deepcopy
from random import shuffle
from algorithm import Person
from algorithm import Topic
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
                if not s.empty and s.person == None:
                    s.person = p
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
            if s.person:
                retval.append(s.person)
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
            if s.person == person:
                s.getNeighbour(self).topic = topic
                return
                    
        raise Exception("couldn't assign topic to person")

    """
    switches the topics, if a second edge is given, the persons are switch to
    """
    def switchAssignments(self, rhs, edge = None):
        topic = rhs.topic
        rhs.topic = self.topic
        self.topic = topic
        if edge:
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
        self.person = None
        self.empty = False  #True if person keeps None
        self.edge1 = None   #First edge/ topic
        self.edge2 = None   #second edge/ topic
        self.position = position   #position in geometry

    def debugName(self, topic = None):
        if topic and self.person:
            return "Empty: " + str(self.empty) + " " + str(self.edge1.index) + "," + str(self.edge2.index) + \
                ", Name: " + self.person.name + ", Rank(" + str(self.person.getRank(topic)) + ")"
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
    
    """
    switches the assigned persons
    """
    def switchPerson(self, rhs):
        person = self.person
        self.person = rhs.person
        rhs.person = person

    def getSatisfaction(self):
        if self.person:
            return self.person.satisfaction(self.edge1.getTopic(), self.edge2.getTopic())
        return 100
    
    def switchIfBetter(self, rhs):
        current = self.getSatisfaction() + rhs.getSatisfaction()
        
        tmp = self.person.satisfaction(rhs.edge1.getTopic(), rhs.edge2.getTopic())
        tmp = tmp + rhs.person.satisfaction(self.edge1.getTopic(), self.edge2.getTopic())

        if current > tmp:
            p = self.person
            self.person = rhs.person
            rhs.person = p


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

    def assignPerson(self, p):
        if self.person == None:
            self.person = p
        else:
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
    initializes the edges with color and index
    
    params
    """
    def basic(self):
        #create topics with colors
        for c in self.colors:
            t = Edge("-", self.colors[c], c)
            self.edges.append(t)

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
            print("Debug empty", empty) 
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
            if s.person:
                sat = sat + s.getSatisfaction()
                print(s.person.name, s.getSatisfaction())
                i = i + 1

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
            retval.append([self.edges[self.colors[t[0]]-1], self.edges[self.colors[t[1]]-1]])
        return retval

    def printAgenda(self):
        agenda = self.getAgenda()
        for h in agenda:
            print("-----")
            print(h[0].color, h[0].topic.name if h[0].topic else None)
            for s in h[0].struts:
                print("  ", s.debugName(h[0].topic))
            print(h[1].color, h[1].topic.name if h[1].topic else None)
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
        head = Topic.getLeastPopular(topics, persons)
        edge.assignTopic(head)
        topics.remove(head)
        
        #select persons who likes center topic most
        pers = head.nPersonsLikeTopic(persons, edge.getNumConnected())
        
        #assign persons to struts of edge
        edge.assignPersons(pers)
        for p in pers:
            print(p.name)
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
                    if s.position in self.sets[0]:
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
        tmp = start #start strut
        pers = None
        left = len(ring_topics)

        while True:
            #close strut (last strut)
            #if tmp.getLeftStrut(ring_struts) == start and not tmp.isEmpty():
            if left < 2 and not tmp.isEmpty():
                #if less than optimize number of persons, edge could be unsigned
                if tmp.getRight().getTopic() == None:
                    pers = tmp.getLeft().getTopic().nPersonsLikeTopic(persons, 1)[0]
                    t = pers.getMostBeautyfulTopic(topics)
                    tmp.getRight().assignTopic(t)
                    tmp.assignPerson(pers)
                    #topic no longer selectable
                    topics.remove(t)
                    persons.remove(pers)
                else:
                    p = tmp.assignPersonFromList(persons)
                    persons.remove(p)
            elif not tmp.isEmpty():

                ring_topics.remove(topic)

                pers = topic.nPersonsLikeTopic(persons, 1)[0]
                print("DEBUG: topic", topic.name," Pers:" ,pers.name)
                persons.remove(pers)
                tmp.assignPerson(pers)

                #switch topics from edge to edge
                #alternative edge1.switchWithTopic(topic, ring_edges, edge)
                edge1 = tmp.getRight()
                edge2 = None
                for e in ring_edges:
                    if topic == e.getTopic():
                        edge2 = e

                #check if edge is correct, should not happen
                if edge2 == None:
                    raise Exception("Edge is empty")
                if edge1.index != tmp.position[1]:
                    raise Exception("edge does not match empty")
                
                edge1.switchAssignments(edge2, edge)
                topic = pers.getMostBeautyfulTopic(ring_topics)
            else:
                print("EMPTY")


                #if edge.pos == pos:
            left = left - 1
            tmp = tmp.getLeftStrut(ring_struts)
            if tmp == start:
                return None #break

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


class Oktaeder2(Structure2):
    def __init__(self, persons = 12):
        Structure2.__init__(self, 12)
        self.numTopics = 6
        self.minPersons = 11
        self.maxPersons = 12
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
        self.optimize()
        self.optimize()

        #self.build_ring(_topics, _persons, self.edges[0].opposite())
        #close()

if __name__ == '__main__':
    o = Oktaeder2()
    o.random_init(12)
    o.build()
    #o.basic()
    #o.create()
    o.printAgenda()


class Person:
    def __init__(self, name):
        self.name = name
        self.priorityList = []
        self.topic_A = None
        self.topic_B = None
        self.strut = None
        self.rang_A = 0
        self.rang_B = 0

    def random(self, num):
        for i in range(1, num + 1):
            self.priorityList.append(i)

        shuffle(self.priorityList)

    def listinput(self, l):
        for i in l:
            self.priorityList.append(int(i))
        print(self.name, self.priorityList)
    
    #returns the most beautiful topic from a list of topics
    def getMostBeautyfulTopic(self, topics):
        #iterate through topic list
        for prio in self.priorityList:
            for t in topics:
                if t.index == prio:
                    return t
        print("ERROR 1", self.name)
        return None

    def out(self, fobj = None):
        if fobj == None:
            print(self.name, self.priorityList)
        else:
            #fobj.write(self.name + ";" + str(self.priorityList) + "\n")
            fobj.write(self.name)
            for t in self.priorityList:
                fobj.write(";" + str(t))
            fobj.write("\n")

    def assignToTopic(self, topic):
        if self.topic_A == None:
            self.topic_A = topic
            self.rang_A = self.getRank(topic)
        elif self.topic_B == None:
            self.topic_B = topic
            self.rang_B = self.getRank(topic)
        else:
            print("ERROR 2", self.name)
            out

    def clear(self):
        r1 = self.topic_A
        r2 = self.topic_B
        if self.topic_A != None:
            self.topic_A.removeAssignment(self)
            self.topic_A = None
            self.rang_A = 0
        if self.topic_B != None:
            self.topic_B.removeAssignment(self)
            self.topic_B = None
            self.rang_B = 0

        return r1, r2

    def removeAssignment(self, topic):
        if self.topic_A == topic:
            self.topic_A = None
            self.rang_A = 0
        elif self.topic_B == topic:
            self.topic_B = None
            self.rang_B = 0 
        else:
            print("ERROR 3", self.name)
            out

    def print_static(self):
        if self.topic_A == None or self.topic_B == None:
            print(self.name, self.satisfaction(), "-")
        else:
            print(self.name, self.satisfaction(), self.topic_A.color, "(", self.rang_A, ")", self.topic_B.color, "(", self.rang_B, ")")
        #print(" ", self.topic_A.name, self.rang_A)
        #print(" ", self.topic_B.name, self.rang_B)

    def satisfaction(self, t1 = None, t2 = None):
        if t1 == None:
            t1 = self.topic_A
        if t2 == None:
            t2 = self.topic_B
        #if t1 == None or t2 == None:
        #    return None
        return self.getRank(t1) + self.getRank(t2)
        #return self.rang_A + self.rang_B

    def getNext(self, topic):
        if self.topic_A == topic:
            return self.topic_B
        elif self.topic_B == topic:
            return self.topic_A
        return None

    def getRank(self, topic):
        if topic == None:
            return len(self.priorityList) + 1
        for i in range(len(self.priorityList)):
            if self.priorityList[i] == topic.index:
                return i + 1
        return len(self.priorityList) + 1

    def getStrutAsString(self):
        return self.topic_A.color + " - " + self.topic_B.color

    def getStrut(self):
        if self.topic_A == None or self.topic_B == None:
            return None
        return (self.topic_A.color, self.topic_B.color)

    def switchIfBetter(self, p2):
        current = self.satisfaction() + p2.satisfaction()
        
        tmp = self.getRank(p2.topic_A) + self.getRank(p2.topic_B)
        tmp = tmp + p2.getRank(self.topic_A) + p2.getRank(self.topic_B)

        if tmp < current:
            print("--SWITCH--")
            tmp_a1, tmp_b1 = p2.clear()
            tmp_a2, tmp_b2 = self.clear()
            if tmp_a1 != None:
                tmp_a1.assignPerson(self)
            if tmp_b1 != None:
                tmp_b1.assignPerson(self)
            if tmp_a2 != None:
                tmp_a2.assignPerson(p2)
            if tmp_b2 != None:
                tmp_b2.assignPerson(p2)


    @staticmethod
    def getMostSatisfied(persons, topic1, topic2):
        rank = 1000
        pers = None
        for p in persons:
            r = p.getRank(topic1) + p.getRank(topic2)
            if r < rank:
                pers = p
                rank = r
        return pers, rank
    
    #struts: tupple of Topics
    @staticmethod
    def getBest(persons, struts):
        retval = []
        for s in struts:
            p, s = getMostSatisfied(persons, s[0], s[1])
            retval.append((p, s[0], s[1]))

class Topic:
    def __init__(self, name, index):
        self.name = name
        self.index = index
        self.persons = []
        self.color = None

    def assignPerson(self, p):
        self.persons.append(p)
        p.assignToTopic(self)

    def removeAssignment(self, p):
        self.persons.remove(p)
        #p.removeAssignment(self)
    
    def assignPersons(self, pl):
        for p in pl:
            self.assignPerson(p)

    #return (one)connected topic by a person from list
    def getNext(self, persons):
        for p in persons:
            if p in self.persons:
                return p.getNext(self), p

    #returns n persons who like topic most
    #list is reverse sorted (person who dislike most is at first position)
    def nPersonsLikeTopic(self, persons, num):
        retval = []
        count = 0
        for i in range(len(persons[0].priorityList)):
            for p in persons:
                if self.index == p.priorityList[i]:
                    retval.insert(0, p)
                    count = count + 1
                if count == num:
                    return retval


    def print(self):
        print("------------------")
        print(self.color, ":")
        print("  Name:", self.name)
        print("  Members:")
        for p in self.persons:
            print("    ", p.name, ",", p.getRank(self), p.getStrutAsString())

    #calculates least popular topic    
    @staticmethod
    def getLeastPopular(topics, persons):
        #sizeof array y= remaining topics, x = num of topics plus column for topic index
        numTopics = len(persons[0].priorityList)
        count = np.zeros((len(topics), numTopics+1), int)
        row = -1
        for t in topics:
            #write index into first column
            row = row + 1
            count[row][0] = t.index
            for p in persons:
                #iterate through the prioritylist of each person
                #and increment the topic at position of priority 
                for pindex in range(len(p.priorityList)):
                    if p.priorityList[pindex] == t.index:
                        count[row][pindex+1] = count[row][pindex+1] + 1
                        break
        il = count[:,0]
        accu = np.cumsum(count[:,1:],1)

        #calculate popularity
        pop = np.cumsum(accu,1)[:,numTopics-1]
        least_pop = il[np.argmin(pop)]

        pop = np.vstack([il,pop]).transpose()
        print(pop)
        print("Least Popular Topic:", least_pop)
        
        for t in topics:
            if t.index == least_pop:
                retval = t
                return t

        return None


class StructureTest:
    def __init__(self, colors, struts):
        self.structure = []
        #Ikosaeder
        self.colors = colors
        self.struts = struts 

    """
    tests if all struts are dipicted by the connections between the persons
    """
    def test(self, persons):
        pers = persons[:]
        struts = self.struts[:]
        errors = 0
        for p in persons:
            strut = p.getStrut()
            if strut == None:
                continue
            tmp1 = self.colors[strut[0]]
            tmp2 = self.colors[strut[1]]
            if tmp1 is None or tmp2 is None:
                errors = errors + 1
                print("Error:", "no strut for person:", p.name)
            
            n1 = min(tmp1,tmp2)
            n2 = max(tmp1,tmp2)
            if (n1,n2) in struts:
                struts.remove((n1,n2))
            else:
                errors = errors + 1
                print("Error:", strut, "not in list", (n1,n2))

        for s in struts:
                errors = errors + 1
                print("Error:", "no person for strut", s)
        
        print("Errors:", errors)
        return errors
        
            

    def translate(self):
        self.struts = []
        for s in self.connections:
            self.struts.append((self.colors[s[0]],self.colors[s[1]]))

            
class Ring:
    def __init__(self):
        self.head = None
        self.pers = []
        self.ring = []
        self.start = None

    """
    connects two Rings with a zickzack line
    
    params
    ------
    rhs: Ring
        right hand side ring
    person: Person[]
        list of persons that can be used

    return
    ------
    Person[]: list of assigned Persons
    """
    def connect(self, rhs, persons):
        _persons = persons[:]
        _startpoint = Topic.getLeastPopular(self.ring + rhs.ring, _persons)
        if _startpoint in self.ring:
            upper_ring = self
            lower_ring = rhs
        else:
            upper_ring = rhs
            lower_ring = self

        _pers = _startpoint.nPersonsLikeTopic(_persons, 2)

        #make the v-connection but do not connect, find only position
        last = lower_ring.ring[-1]
        strut = (1000, 0)

        for t in lower_ring.ring:
            tmp = self.vStrut(_pers[0], _pers[1], _startpoint, last, t)
            if tmp[0] < strut[0]:
                strut = tmp
            last = t

        #add person to strut
        self.activate(_persons, strut[1])
        self.activate(_persons, strut[2])
    
        if lower_ring.getNextTopic(strut[1][2]) == strut[2][2]:
            left = strut[1][2]
            right = strut [2][2]
        else:    
            left = strut[2][2]
            right = strut [1][2]
        
        print("V: ", _startpoint.name, upper_ring.ring.index(_startpoint))    
        print("E: ", left.name, lower_ring.ring.index(left))    
        print("E: ", right.name, lower_ring.ring.index(right))    

        upper_ring.start = _startpoint
        direction = "right"
        
        #create struts, both rings right direction
        struts = self.createZickZackEx(upper_ring, lower_ring,_startpoint,right,"right")
        #assign persons to struts
        sat, res = self.getBest(_persons,struts)
        lower_ring.start = right

        #create struts, one ring right direction, one ring left
        struts = self.createZickZackEx(upper_ring, lower_ring,_startpoint,left,"left")
        #assign persons to struts
        satl, resl = self.getBest(_persons,struts)

        #take connection with more satisfaction
        if satl < sat:
            direction = "left"
            res = resl
            lower_ring.start = left
            lower_ring.ring = list(reversed(lower_ring.ring))

        retval = []
        for r in res:
            retval.append(self.activate(_persons,r))

        return upper_ring, lower_ring, direction, retval

    def createZickZack(self, ring_upper, ring_lower, start_upper, start_lower, direction):
        struts = []
        tmp_upper = start_upper
        tmp_lower = start_lower
        while True: 
            struts.append((tmp_upper, tmp_lower))
            tmp_upper = ring_upper.getNextTopic(tmp_upper)
            struts.append((tmp_upper, tmp_lower))
            if direction == "right":
                tmp_lower = ring_lower.getNextTopic(tmp_lower)
            else:
                tmp_lower = ring_lower.getPrevTopic(tmp_lower)
            if start_upper == tmp_upper:
                break

        return struts

    #creates ZickZack but excludes V connection (speed optimization)
    def createZickZackEx(self, ring_upper, ring_lower, start_upper, start_lower, direction):
        struts = []
        tmp_upper = ring_upper.getNextTopic(start_upper)
        if direction == "right":
            tmp_lower = start_lower
            end = ring_lower.getPrevTopic(start_lower)
        else:
            #tmp_upper = ring_upper.getPrevTopic(start_upper)
            tmp_lower = start_lower
            end = ring_lower.getNextTopic(start_lower)
        while True:
            struts.append((tmp_upper, tmp_lower))
            if direction == "right":
                tmp_lower = ring_lower.getNextTopic(tmp_lower)
            else:
                tmp_lower = ring_lower.getPrevTopic(tmp_lower)
            struts.append((tmp_upper, tmp_lower))
            tmp_upper = ring_upper.getNextTopic(tmp_upper)
            if end == tmp_lower:
                break

        return struts
    """
    creates two struts e1-v and v-e2
    """
    def vStrut(self, p1, p2, v, e1, e2):
        sat1 = p1.satisfaction(v, e1) + p2.satisfaction(v, e2)
        sat2 = p1.satisfaction(v, e2) + p2.satisfaction(v, e1)

        if sat1 < sat2:
            return (sat1, (p1, v, e1), (p2, v, e2))
        else:
            return (sat2, (p1, v, e2), (p2, v, e1))

    #removes Person from list and assigns to topics(strut)
    def activate(self, pers, ptt):
        pers.remove(ptt[0])
        ptt[1].assignPerson(ptt[0])
        ptt[2].assignPerson(ptt[0])
        return ptt[0]
        

    def getBest(self, pers, struts):
        if len(struts) == 1:
            strut = struts[0]
            p, sat = Person.getMostSatisfied(pers, strut[0], strut[1])
            #todo, do not check only for satisafaction but to for least satisfaction
            return sat, [(p, strut[0], strut[1])]

        satisfaction = 10000
        retval = []
        max_pers = 20

        for s in struts:
            _struts = struts[:]
            _pers = pers[:]
            _struts.remove(s)
            p, sat = Person.getMostSatisfied(_pers, s[0], s[1])
            _pers.remove(p)
            sat2, tub =  self.getBest(_pers, _struts)
            if sat2 + sat < satisfaction:
                satisfaction = sat2 + sat
                retval = tub + [(p, s[0], s[1])]

        return satisfaction, retval
        

    def build(self, topics, persons, num_ring_topics):
        #do not change original
        _topics = topics[:]
        _persons = persons[:]

        #select least popular topic as center
        self.head = Topic.getLeastPopular(_topics, _persons)
        self.head.color ="white"
        _topics.remove(self.head)
        #select persons who likes center topic most
        self.pers = self.head.nPersonsLikeTopic(_persons, num_ring_topics)
        self.head.assignPersons(self.pers)

        for p, t in self.selectStarTopics(_topics, self.pers, self.head):
            #select topics to already choosed people
            self.ring.append(t)
            _topics.remove(t)
            t.assignPerson(p)
            _persons.remove(p)

        return [self.head] + self.ring, self.pers
        #self.closeRing(_persons)

    def closeRing(self, persons):
        _persons = persons[:]
        #select for sorting
        _ring_persons = []
        #debug
        print("DEBUG::")
        for p in persons:
            print(p.name)
        print("DEBUG::")
        for p, t1, t2 in self.selectRingPersons(self.ring, persons):
            #select people to already selectd ring topics
            print("DEBUG::N", p.name, t1.name, t2.name)
            t1.assignPerson(p)
            t2.assignPerson(p)
            _ring_persons.append(p)
            self.pers.append(p)
            _persons.remove(p)
            if len(_persons) == 0:
                #if number of persons is less than
                #optimal number
                break

        #sort ring
        _ring = []
        t = self.ring[0]
        _ring.append(t)
        self.ring.remove(t)
        retval = _ring_persons[:]
        #TODO: sorting if not a ring 
        print(len(self.ring),len(_ring_persons))
        while len(self.ring) > 0 and len(_ring_persons) > 0:
            print(len(self.ring),len(_ring_persons))
            t, p = t.getNext(_ring_persons)
            _ring.append(t)
            self.ring.remove(t)
            _ring_persons.remove(p)

        self.ring = _ring
        print("DEBUG::")
        for p in retval:
            print(p.name)
        print("DEBUG::")
        return None, retval

    """
    assigns a color to each tobic
    
    params
    ------
    colors    list of colors, first one is assigned to head topic
    """
    def colorize(self, colors):
        self.head.color = colors[0]
        #if no special startpoint is given, start with first topic
        if self.start is None:
            self.start = self.ring[0]
        tmp = self.start
        for c in colors[1:]:
            print(c)
            tmp.color = c
            tmp = self.getNextTopic(tmp)

    def getNextTopic(self, topic):
        index = self.ring.index(topic)
        if index + 1 == len(self.ring):
            return self.ring[0]
        else:
            return self.ring[index + 1]

    def getPrevTopic(self, topic):
        index = self.ring.index(topic)
        return self.ring[index-1]

    #sorts a list of topics into a ring(4 or 5 topics) and build the struts
    def selectRingPersons(self, topics, persons):
        _topics = topics[:]
        _persons = persons[:]
        close = False if len(persons) < len(topics) else True
        retval = []
        #start with least popular topic
        lp = Topic.getLeastPopular(_topics, _persons)
        _topics.remove(lp)
        print("X DEBUG:", len(_persons))
        #TODO ONE Person
        #optimization, add two person two least pop
        pers = lp.nPersonsLikeTopic(_persons, 2)
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


    #assign a star around a topic (persons already included)
    def selectStarTopics(self, topics, persons, center = None):
        topics = topics[:]

        #sort by center
        if center is not None:
            persons.sort(key=operator.methodcaller("getRank", center), reverse=True)

        assignment = []
        for p in persons:
            t = p.getMostBeautyfulTopic(topics)
            #topic no longer selectable
            topics.remove(t)
            assignment.append((p,t))

        return assignment

class Star:
    def __init__(self):
        num = None
        self.head = None
        self.sat = None
        self.pers = []

    def build(self, center, topics, persons):
        _persons = persons[:]
        self.head = center
        self.sat = topics
        for t in topics:
            p, s = Person.getMostSatisfied(_persons, center, t)
            t.assignPerson(p)
            center.assignPerson(p)
            self.pers.append(p)
            _persons.remove(p)
            if len(_persons) == 0:
                #if number of persons is less than
                #optimal number
                break

        return [self.head], self.pers

    def set_head_color(self, color):
        self.head.color = color

class Structure:
    def __init__(self):
        self.numTopics = 0        
        self.numPersons = 0
        self.type = ""
        self.struts = None
        self.colors = None
        self.persons = None
        self.test = None
        self.opposites = None    
    
    """
    prints the satisfaction from all persons and calculates the average
    
    params
    ------

    return
    ------
    int average satisfaction
    """
    def printStatistics(self):
        mins = 0
        sat = 0
        self.persons.sort(key=operator.methodcaller("satisfaction"), reverse=True)
        for p in self.persons:
            s =  p.satisfaction()
            p.print_static()
            if s == None:
                continue
            sat = sat + s
            if s > mins:
                mins = s
                lp = p

        print("average satisfaction: ", sat/self.numPersons)
        print("less satisfied person: ")
        lp.print_static()

    def optimize(self, pers = None):
        #if pers is None:
        #    pers = self.ring.pers + self.star.pers
        
        pers.sort(key=operator.methodcaller("satisfaction"), reverse=True)

        for p1 in pers:
            for p2 in pers:
                if p1 == p2:
                    continue
                p1.switchIfBetter(p2)
    
    def test(self):
        t = StructureTest(self.colors, self.struts)
        return t.test(self.persons)
    
    """
    fuction to print out some special information
    """
    def printAdditional(self):
        return None

    """
    creates an object by name or number of topics
    """
    def factory(t):
        if t == "O" or t == "OKTAEDER" or t == 6:
            return Oktaeder()
        if t == "I" or t == "IKOSAEDER" or t == 12:
            return Ikosaeder()

    def getNumTopics(self):
        return self.numTopics

    def getMinPersons(self):
        return self.minPersons

    def getMaxPersons(self):
        return self.maxPersons
    
    """
    reads the priority list from a two dimensional array
    each line is one Person

    params
    -------
    array: two dimensional array
        line: Person ID; topic one; topic 2; ...
    """
    def array_init(self, array):
        self.orig_persons = []
        self.orig_topics = []
        for line in array:
            p = Person(line[0])
            p.listinput(line[1:])
            self.orig_persons.append(p)
        
        for i in range(1, self.numTopics + 1):
            name = "T_" + str(i).zfill(2)
            p = Topic(name, i)
            self.orig_topics.append(p)

        return None
        
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
    
    """
    [
    [[Topic 1],[Opposite]],
    [[Topic 2],[Opposite]],
    ...
    ]
    """
    def getAgenda(self):
        self.build(self.orig_topics, self.orig_persons)
        retval = []
        for t in self.opposites:
            retval.append([self.getTopicByColor(t[0]), self.getTopicByColor(t[1])])
        return retval

    def getTopicByColor(self, color):
        print(color)
        for t in self.topics:
            #print("C: ", t.color)
            if t.color == color:
                return t
        return None

class Ikosaeder(Structure):
    def __init__(self, persons = 30):                
        self.numTopics = 12
        self.numPersons = persons
        self.minPersons = 30
        self.maxPersons = 30
        self.type = "Ikosaeder"
        self.upper = None
        self.lower = None
        self.upper_colors = [ "white", "black", "silver", "green", "brown", "dark blue" ]
        self.lower_colors = [ "red", "orange", "gold", "light blue", "purple", "yellow" ]
        #all colors and struts
        self.colors = { "white" : 1, "black" : 2, "silver" : 3, "green" : 4, "brown" : 5, "dark blue" : 6, 
            "red" : 7, "orange" : 8 , "gold" :9, "light blue" : 10, "purple" : 11, "yellow" : 12 }
        self.struts = [(1,2),(1,3),(1,4),(1,5),(1,6),
                   (2,3),(3,4),(4,5),(5,6),(2,6),
                   (2,12),(6,12),(6,11),(5,11),(5,10),
                   (4,10),(4,9),(3,9),(3,8),(2,8),
                   (8,9),(9,10),(10,11),(11,12),(8,12),
                   (7,8),(7,9),(7,10),(7,11),(7,12)]

    def build(self, topics, persons):
        self.topics = deepcopy(topics)
        self.persons = deepcopy(persons)
        comp_t = self.topics[:]
        comp_p = self.persons[:]
        
        #build upper ring/pentagon
        upper = Ring()
        t, p = upper.build(self.topics, self.persons, 5)
        self.clear(t, p)
        t, p = upper.closeRing(self.persons)
        self.optimize(p)
        self.clear(t, p)

        #self.optimize(ring.pers + star.pers)

        #build lower ring/pentagon
        lower = Ring()
        t, p = lower.build(self.topics, self.persons, 5)
        self.clear(t, p)
        t, p = lower.closeRing(self.persons)
        self.clear(t, p)
        self.optimize(p)

        self.upper, self.lower, self.direction, self.zickzack = lower.connect(upper,self.persons)
        self.optimize(self.zickzack)
        #self.upper.colorize(self.upper_colors)    
        #self.lower.colorize(self.lower_colors)    
        
        self.topics = comp_t
        self.persons = comp_p
        self.optimize(self.persons)
        self.upper.colorize(self.upper_colors)    
        self.lower.colorize(self.lower_colors)    
    
    def clear(self, topics, pers):
        if topics is not None:
            for t in topics:
                self.topics.remove(t)
        if pers is not None:
            for p in pers:
                self.persons.remove(p)

    def printAdditional(self):
        print("Direction: ", self.direction)
    
    def printStructure(self):
        print("-Ikosaeder--------------------------------------------")
        self.upper.head.print()    
        for t in self.upper.ring:
            t.print()
        self.lower.head.print()    
        for t in self.lower.ring:
            t.print()
        print("-----------------------------------------------------")

class Oktaeder(Structure):
    def __init__(self, persons = 12):
        self.numTopics = 6
        self.minPersons = 11
        self.maxPersons = 12
        self.numPersons = persons
        self.topics = None
        self.persons = None
        self.type = "Oktaeder"
        self.colors = {"white" : 1, "green" : 2, "blue" : 3, "yellow" : 4, "red" : 5, "black" : 6}
        self.struts = [(1,2),(1,3),(1,4),(1,5),(2,3),(3,4),(4,5),(2,5),(2,6),(3,6),(4,6),(5,6)]
        self.opposites ={ ("white", "black") , ("green", "yellow"), ("blue", "red")}
        self.sets = [[(1,2),(3,4),(5,6)],[(1,2),(4,5),(3,6)],
                        [(1,3),(2,5),(4,6)],[(1,3),(4,5),(2,6)]]
        #parts (1,2), (3,4), (5,6)
        #             (4,5), (3,6)
        #      (1,3), (4,5), (2,6)
        #             (2,5), (4,6)
        #      (1,4), (2,5), (3,6)
        #             (2,3), (5,6)
        #      (1,5), (2,3), (4,6)
        #             (3,4), (2,6)
        
        #opposites: 1-6, 2-4, 3-5

    def build(self, topics, persons):
        self.var = 1
        self.ring,self.star,s1 = self.variants(topics, persons, 1)
        r2,t2,s2 = self.variants(topics, persons, 2)

        if s1 > s2:
            self.ring = r2
            self.star = t2
            self.var = 2

        self.colorize()

        self.topics = [self.ring.head, self.star.head] + self.ring.ring 

    """
    assagins a color to each topic
    
    """
    def colorize(self):
        colors = []
        for k,v in sorted(self.colors.items(), key=operator.itemgetter(1)):
            colors.append(k)
        self.ring.colorize(colors[0:-1])
        self.star.set_head_color(colors[-1])

    def variants(self, topics, persons, var):
        #current architecture: 
        # 1 create a star with ring
        # 2 create a star and connect to ring

        #Build both and select better

        self.topics = deepcopy(topics)
        self.persons = deepcopy(persons)

        #build ring
        ring = Ring()
        t, p = ring.build(self.topics, self.persons, 4)

        #remove objects, that next step uses only remainig
        #self.topics.remove(ring.head)
        self.clear(t, p)
        if var == 1:
            t, p = ring.closeRing(self.persons)
            self.clear(t, p)
        star = Star()
        t, p = star.build(self.topics[0], ring.ring, self.persons)
        self.clear(t, p)
        
        if var != 1:
            t, p = ring.closeRing(self.persons)
            self.clear(t, p)

        self.optimize(ring.pers + star.pers)
        self.ring = ring
        self.star = star

        return ring, star, self.getSatisfaction()

    def clear(self, topics, pers):
        if topics is not None:
            for t in topics:
                self.topics.remove(t)
        if pers is not None:
            for p in pers:
                self.persons.remove(p)

    def getSatisfaction(self):
        self.persons = self.ring.pers + self.star.pers
        sat = 0
        i = 0
        for p in self.persons:
            sat = sat + p.satisfaction()
            i = i + 1

        self.satisfaction = sat/i
        return self.satisfaction

    def optimizeRing(self):
        #self.persons = self.ring.pers + self.star.pers
        self.persons = self.star.pers
        self.persons.sort(key=operator.methodcaller("satisfaction"), reverse=True)

        print("Optimize")
        print(" Satisfaction 1:", self.getSatisfaction())

        for p1 in self.persons:
            for p2 in self.persons:
                if p1 == p2:
                    continue
                p1.switchIfBetter(p2)

    def optimize(self, pers = None):
        if pers is None:
            pers = self.ring.pers + self.star.pers
        
        pers.sort(key=operator.methodcaller("satisfaction"), reverse=True)

        for p1 in pers:
            for p2 in self.persons:
                if p1 == p2:
                    continue
                p1.switchIfBetter(p2)

    """
    [
    [Topic 1,Opposite],
    [Topic 2,Opposite],
    ...
    ]
    """
    def _getAgenda(self):
        #opposites: white-black, green-yellow, blue-red
        #opposites: 1-6, 2-4, 3-5
        retval = [[self.getTopicByColor("white"), self.getTopicByColor("black")],
                 [self.getTopicByColor("green"), self.getTopicByColor("yellow")],
                 [self.getTopicByColor("blue"), self.getTopicByColor("red")]]
        return retval
 
    def printStructure(self):
        print("-Oktaeder--------------------------------------------")
        self.ring.head.print()    
        for t in self.ring.ring:
            t.print()
        self.star.head.print()    
        print("-----------------------------------------------------")
        
    def printSatisfaction(self):    
        sat = 0
        i = 0
        print("Ring:")
        for p in self.ring.pers:
            p.print_static()
            sat = sat + p.satisfaction()
            i = i + 1
        print("-------------------------------")
        print("Star:")
        for p in self.star.pers:
            p.print_static()
            sat = sat + p.satisfaction()
            i = i + 1

        self.satisfaction = sat/i
        print("Satisfaction:", self.satisfaction)

class IkoTest:
    def __init__(self, themen=6, persons=12):
        self.numTopics = themen
        self.numPersons = persons
        self.persons = []
        self.persons_stat = []
        self.topics = []
        if self.numTopics == 12:
            self.struct = Ikosaeder() 
        if self.numTopics == 6:
            self.struct = Structure.factory("O") #Oktaeder()

    def file_init(self, filename):
        fobj = open(filename)
        for line in fobj:
            p = Person(line.split(';')[0])
            p.listinput(line.split(';')[1:])
            self.persons.append(p)
            self.persons_stat.append(p)
        
        for i in range(1, self.numTopics + 1):
            name = "T_" + str(i).zfill(2)
            p = Topic(name, i)
            self.topics.append(p)

        return None
    
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
            self.persons.append(p)
            self.persons_stat.append(p)
        
        for i in range(1, self.numTopics + 1):
            name = "T_" + str(i).zfill(2)
            p = Topic(name, i)
            self.topics.append(p)

        return None

    #init the person table with random priority list
    def random_init(self):
        for i in range(0, self.numPersons):
            name = "P_" + str(i).zfill(2)
            p = Person(name)
            p.random(self.numTopics)
            self.persons.append(p)
            self.persons_stat.append(p)
        
        for i in range(1, self.numTopics + 1):
            name = "T_" + str(i).zfill(2)
            p = Topic(name, i)
            self.topics.append(p)

    def run(self):
        self.struct.build(self.topics, self.persons)
        self.struct.printStructure()
        self.struct.printStatistics()
        self.struct.printAdditional()

        for t in self.struct.getAgenda():
            print(t[0].color)
            for p in t[0].persons:
                print(" ", p.name)
            print(t[1].color)
            for p in t[1].persons:
                print(" ", p.name)
            print("---------------------")

    def test(self):
        err = self.struct.test()
        if err > 0:
            fobj = open("yellow_err.txt", "w")
            print("Failed")
        else:
            fobj = open("yellow.txt", "w")
            print("OK")

        for p in self.persons:
            p.out(fobj)

def test3():
    struct = Structure.factory("O")
    struct.random_init(11)
    agenda = struct.getAgenda()
    print("---------------------")
    for t in agenda:
        print(t[0].color, t[0].name)
        for p in t[0].persons:
            print(" ", p.name)
        print(t[1].color, t[1].name)
        for p in t[1].persons:
            print(" ", p.name)
        print("---------------------")
    return True

def test2():
    arr = [[1, 2, 3, 1, 5, 4, 6], [2, 6, 5, 4, 1, 2, 3], [3, 2, 4, 3, 1, 5, 6], [4, 4, 5, 3, 1, 2, 6], [5, 1, 2, 3, 4, 5, 6], [6, 1, 3, 5, 4, 6, 2], [7, 2, 4, 1, 3, 5, 6], [8, 6, 2, 3, 1, 4, 5], [9, 3, 6, 1, 2, 4, 5], [10, 5, 3, 4, 1, 2, 6], [11, 6, 1, 2, 3, 4, 5], [12, 1, 2, 3, 4, 5, 6]]
    struct = Structure.factory("O")
    struct.array_init(arr)
    agenda = struct.getAgenda()
    print("---------------------")
    for t in agenda:
        print(t[0].color)
        for p in t[0].persons:
            print(" ", p.name)
        print(t[1].color)
        for p in t[1].persons:
            print(" ", p.name)
        print("---------------------")
    return True



"""
    filename = None
    for i in range(len(sys.argv)):
        if sys.argv[i] == "-f":
            filename = sys.argv[i+1]

    t = IkoTest(6, 12)
    #t = IkoTest(12, 33)
    if filename is None:
        t.random_init():
    else:
        t.file_init(filename)
    t.run()
    t.test()
"""
