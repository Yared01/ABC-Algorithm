#!/usr/bin/python3
import source as food
import quick_psort2 as psort
import quick_fsort2 as fsort
import math
import random as rand
import numpy as np
class Colony(food.Nectar):
    def __init__(
            self,
            cost_fn,
            lower_limit,
            upper_limit,
            population,
            max_iteration
    ):
        self.a = 1  # accelerator
        self.w_min = 0.4
        self.w_max = 0.9
        self.c1 = 0.01
        self.c2 = 0.01
        self.dimesion = len(lower_limit)
        # population based parameters
        self.cost_of = cost_fn
        self.lower_bound = lower_limit
        self.upper_bound = upper_limit
        self.population = population
        self.nsource = int(round(population / 2))
        # temporal assignment of number of food sources
        self.max_trial = 100#int(round(0.6 * self.dimesion * population / 2))
        self.max_rerun = max_iteration
        self.optimal = food.Nectar([0.0]*self.dimesion)
        self.suboptimal = food.Nectar([0.0]*self.dimesion)
        self.bee = []

    # GETTERS and SETTERS
    def get_optimal(self):
        return self.optimal

    def get_suboptimal(self):
        return self.suboptimal

    def get_dimension(self):
        return self.dimesion

    def get_nsource(self):
        return self.nsource

    def get_upper_bound(self):
        return self.upper_bound

    def get_lower_bound(self):
        return self.lower_bound

    def set_upper_bound(self, Ubound):
        self.upper_bound = Ubound

    def set_lower_bound(self, Lbound):
        self.lower_bound = Lbound

    def get_max_rerun(self):
        return self.max_rerun

    def get_max_trial(self):
        return self.max_trial

    def get_index(self, min_fitness):
        # the fuction return the index which exactly exceed a
        # minimum probability
        x = 0
        while self.bee[x].get_fitness() < min_fitness:
            x += 1
        return x

    # SYSTEM FUNCTIONS
    def random_nominee_except(self, index):
        nominees = list(range(self.get_nsource()))
        # Isolate the excluded nominees
        nominees.remove(index)
        return rand.choice(nominees)

    def band_filter(self, new_soln):
        ubound = self.get_upper_bound()
        lbound = self.get_lower_bound()
        for i in range(self.get_dimension()):
            if new_soln[i] > ubound[i]:
                new_soln[i] = ubound[i]
            elif new_soln[i] < lbound[i]:
                new_soln[i] = lbound[i]
        return new_soln


    def sort_by_probability(self):
        # sorting with curve fitting taking index as x
        # value of item as y, so y = ax + b to estimated
        # value of index i.e. x from y as x = (y-b)/a
        Qp = psort.Quick(self.bee)
        Qp.psort2(0, self.get_nsource()-1)

    def sort_by_fitness(self):
        # sorting with curve fitting taking index as x
        # value of item as y, so y = ax + b to estimated
        # value of index i.e. x from y as x = (y-b)/a
        Qf = fsort.Quick(self.bee)
        Qf.fsort2(0, self.get_nsource()-1)


    # Generate robability of food source
    def spawn_probability(self):
        total_fitness = 0
        max_fitness = 0
        ith_fitness = 0
        # sum probability
        for i in range(self.get_nsource()):
            ith_fitness = self.bee[i].get_fitness()
            if max_fitness < ith_fitness:
                max_fitness = ith_fitness
                total_fitness += self.bee[i].get_fitness()

        # generate probability
        for j in range(self.get_nsource()):
            jth_probability = self.bee[j].get_fitness()/total_fitness
            self.bee[j].set_probability(jth_probability)

        return max_fitness/total_fitness

    def search_optimal(self):
        """
        search for optimal and suboptimal food source in
        population.
        """

        for i in range(self.get_nsource()):
            ith_bee_fitness = self.bee[i].get_fitness()
            best_fitness = self.optimal.get_fitness()
            if best_fitness < ith_bee_fitness:
                self.suboptimal.greedy_choice(self.optimal)
                self.optimal.greedy_choice(self.bee[i])
            elif best_fitness == ith_bee_fitness:
                pass # protect updating suboptimal in this case
            elif self.suboptimal.get_fitness() < ith_bee_fitness:
                self.suboptimal.greedy_choice(self.bee[i])



    def chaotic_config(self):
        """
        Use chaotic system and opposition based learning to
        initialize the Artificial Bee Colony food source
        """
        #op_bee = food.Nectar([0.0]*self.get_dimension())
        for i in range(self.get_nsource()):
            # STARTING LOOPING
            ch_source = [0.0] * self.get_dimension()
            for j in range(self.get_dimension()):
                # Chaotic Intialization selection
                c_h = rand.uniform(0, 1)
                c_h = math.sin(math.pi * c_h)
                # randomly choose the vector element/parameter to be modified
                # par2chg = int(rand.uniform(0, D))
                ch_source[j] = self.lower_bound[j] + c_h * (self.upper_bound[j]-self.lower_bound[j])

            # END LOOPING
            ch_fsource = self.band_filter(ch_source)
            ch_fcost = self.cost_of(ch_fsource)
            self.bee.append(food.Nectar(ch_fsource, ch_fcost))
            # configure opposition based learning
            pt_src = self.bee[i].get_source()
            #op_source= self.lower_bound+self.upper_bound-self.bee[i].source
            # generate opposition based learning for bees
            op_src = [self.lower_bound[k] + self.upper_bound[k] - pt_src[k]
                      for k in range(self.get_dimension())]
            # filter opposition based sources
            op_source = self.band_filter(op_src)
            op_cost = self.cost_of(op_source)
            op_bee = food.Nectar(op_source, op_cost)
            # greedy selection between Chaotic and Opposition
            self.bee[i].greedy_choice(op_bee)

    def chaotic_search(self, t_run, seq_length = 5):
        # declare chaotic bee
        ch_k = rand.uniform(0,1)
        ch_lambdak = (self.max_rerun - t_run + 1)/ self.max_rerun
        ith_best = self.optimal.get_source()
        new_src = np.array([0.0]*self.get_dimension())
        chv_k = np.array([0.0]*self.get_dimension())
        lbound = self.get_lower_bound()
        ubound = self.get_upper_bound()
        for k in range(seq_length):
            for i in range(self.get_dimension() - 1):
                chv_k[i] = lbound[i] + ch_k * (ubound[i] - lbound[i])
                # generate new candidate food source
                new_src[i] = ith_best[i] + ch_lambdak * (chv_k[i] - ith_best[i])

            new_src = self.band_filter(new_src)
            new_cost = self.cost_of(new_src)
            ch_bee= food.Nectar(new_src, new_cost)
            # greedy selection by optimal soln holder bee
            self.optimal.greedy_choice(ch_bee)
            # greedy choice by suboptimal soln hoder
            self.suboptimal.greedy_choice(ch_bee)

            # update chaotic sequence
            ch_k =  4 * ch_k * (1 - ch_k)


    # Optimal source finder
    def employed_bees_phase(self):
        """
        The Employed or worker bee phase of IABC algorithm
        """
        for i in range(self.get_nsource()):
            # nominate neighbour solution except
            k = self.random_nominee_except(i)
            # randomly select soln vector element xi to change
            xi = rand.randint(0,self.get_dimension()-1)
            phi = self.a * rand.uniform(-1,1)
            # get current food source
            eith_src = self.bee[i].get_source()
            # generate a new solution with all vector element in current
            # vector and change the randomly selected parameter only
            enew_src = np.copy(eith_src)
            ekth_src = self.bee[k].get_source()
            # generate new candidate food source
            enew_src[xi] = eith_src[xi] + phi * (eith_src[xi] - ekth_src[xi])
            # update new soln in range of solution lower_limit
            enew_src = self.band_filter(enew_src)
            enew_cost = self.cost_of(enew_src)
            # generate new bee with new_src

            enew_bee = food.Nectar(enew_src, enew_cost)
            # greedy selection by current employed bee
            self.bee[i].greedy_choice(enew_bee)



    def onlooker_bees_phase(self, t_run):
        # generated and get maximum probability of food sources
        #maxP = self.spawn_probability()
        # sort result in increasing order
        self.sort_by_fitness()
        min_fit = self.bee[0].get_fitness()
        max_fit = self.bee[self.get_nsource()-1].get_fitness()
        # generate the inertia weight that control convergence
        w = self.w_min + t_run * (self.w_max - self.w_min)/self.max_rerun
        for i in range(self.get_nsource()):
            randF = rand.uniform(min_fit, max_fit)
            # estimate starting of prefered food source index
            pivot_index = self.get_index(randF)
            while pivot_index < self.get_nsource():
                phi = self.a * rand.uniform(-1,1)
                si = self.a * rand.uniform(-1,1)
                best_src = self.optimal.get_source() #MARKED as TREAT
                subbest_src = self.suboptimal.get_source()
                pivot_src =  self.bee[pivot_index].get_source()
                # randomly determine the src vector element xi to update
                xi = rand.randint(0, self.get_dimension() - 1)
                # generate a new value of pivoted bee vector element xi
                new_xi = w * best_src[xi] + self.c1*phi*(best_src[xi] - pivot_src[xi])\
                         + self.c2 * si * (subbest_src[xi] - pivot_src[xi])
                pivot_src[xi] = new_xi
                pivot_src = self.band_filter(pivot_src)
                pivot_cost = self.cost_of(pivot_src)
                new_bee = food.Nectar(pivot_src, pivot_cost)
                self.bee[pivot_index].greedy_choice(new_bee)
                tmp_fit = self.bee[pivot_index].get_fitness()
                if tmp_fit > max_fit:
                    max_fit = tmp_fit

                pivot_index += 1

    def scout_bees_phase(self):
        """
        #The food source whose trial limit is reached
        #will randomly reallocate and its trial counter get reset_trial
        """
        ubound = self.get_upper_bound()
        lbound = self.get_lower_bound()
        for i in range(self.get_nsource()):
            if self.bee[i].get_trial() > self.get_max_trial():
                temp  = [lb + rand.uniform(0,1)*(ub - lb) for lb,ub in zip(ubound, lbound)]
                # filter generated food source
                temp_src = self.band_filter(temp)
                temp_cost = self.cost_of(temp_src)
                # updating trail expired solution
                self.bee[i].set_source(temp_src)
                self.bee[i].set_cost(temp_cost)
                self.bee[i].make_fitness()
                # reset trial counter of the trial out solution
                self.bee[i].reset_trial()

    def optimize(self):
        self.chaotic_config()
        for t in range(self.max_rerun):
            #print("Iteration = ", t)
            self.employed_bees_phase()
            self.onlooker_bees_phase(t)
            self.search_optimal()
            self.scout_bees_phase()
            self.chaotic_search(t)

        return self.get_optimal()
