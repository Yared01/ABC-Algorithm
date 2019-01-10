"""
The nectar module for modeling food sources of honey bees
Module name: Nectar
source, fitness(quality), cost of extraction
"""
import numpy as np
class Nectar(object):
    trial_no = 0
    def __init__(self, source, cost = float("inf")):
        self.source = np.copy(np.array(source)) # Just to make sure list is not passed
        self.cost = cost
        self.fitness = self.make_fitness()
        self.probability = 0
        self.trial = Nectar.trial_no

    def set_probability(self, probability):
        self.probability = probability

    def get_probability(self):
        return self.probability

    def set_source(self, new_src):
        self.source = np.array(new_src)

    def get_source(self):
        return np.copy(self.source)

    def set_fitness(self, new_fitness):
        self.fitness = new_fitness

    def get_fitness(self):
        return self.fitness

    def set_cost(self, new_cost):
        self.cost = new_cost

    def get_cost(self):
        return self.cost

    def set_trial(self, new_trial):
        self.trial = new_trial

    def reset_trial(self):
        self.trial = 0

    def get_trial(self):
        return self.trial

    def greedy_choice(self, other):
        if self.fitness < other.get_fitness():
            """
            self.source = other.get_source()
            self.cost = other.get_cost()
            self.fitness = other.get_fitness()
            print("self",self)
            """
            #print("bu_greedy = ", self)
            self.set_source(other.get_source())
            self.set_cost(other.get_cost())
            self.set_fitness(other.get_fitness())
            # reset trial counter to zero for modified system
            Nectar.trial_no = 0
            self.trial = Nectar.trial_no
        elif self.fitness >= other.get_fitness():
            Nectar.trial_no +=1
            self.trial = Nectar.trial_no

    def make_fitness(self):
        
        if self.cost >= 0:
            return 1/(self.cost + 1)
        else:
            return abs(self.cost) + 1
        
        #return(np.exp(-self.cost * self.cost))
        #return 1/(1+(self.cost*self.cost))


    def __repr__(self):
        return "s: %r f: %r c: %r : t = %r" %(self.source, self.fitness, self.cost,self.trial)
