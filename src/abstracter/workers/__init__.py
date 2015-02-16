"""@package workers
Workers and WorkersManager.

@see abstracter.concepts_network.ConceptNetwork
"""
from random import random

MAX_LEN=1000

class WorkerException(Exception):
    pass

class Worker:
    """
    The workers act on several objects : they activate nodes, create some...
    The main class Worker has subclasses for every type of worker.
    """

    def __init__(self, urgency=0):
        self.urgency = urgency

    def run(self, context):
        """
        Launch the worker.
        """
        return 0

    def __str__(self):
        return("Worker, urgency : " + self.urgency)


class WorkersManager:
    """
    The workers manager is a stack of workers which wait to be launched.
    """
    def __init__(self,context):
        self.workers = []
        self.time = 0
        self.context=context


    def pop(self):
        return self.workers.pop(0)

    def pushEnd(self, w):
        if(len(self.workers)<MAX_LEN):
            self.workers.append(w)

    def push(self, w,randomly=True):
        """
        Push a new worker into the queue, depending on its urgency.

        @param randomly When set to false, the stack is like a priority one. 
        When set to true, a random factor is applied.
        """
        if(len(self.workers)<MAX_LEN):
            i = 0
            while i < len(self.workers) and self.workers[i].urgency > w.urgency:
                i += 1
            if(randomly):
                i += int((random() - 0.5) * len(self.workers) / 15)
            self.workers.insert(i, w)

    def isEmpty(self):
        return self.workers==[]

    def runWorker(self,w=None):
        w = w or self.pop()
        delta_time = w.run(self.context)
        self.time += delta_time


    def __str__(self):
        res="WorkersManager : \nTime = "+self.time.__str__() \
        +"\n"+len(self.workers).__str__()+" workers :"
        for w in self.workers:
            res+="\n"+w.__str__()
        return res
