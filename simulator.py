from copy import deepcopy
import numpy as np
import random

from task import Task

class Simulator:

	def __init__(self,scenario,agent):
		self.scenario = scenario
		self.agent = agent

		x,y = agent.position[0],agent.position[1]
		self.scenario.map[x,y] = 2

	def spawn_task(self):
		random_position = self.scenario.get_random_position()

		risc = round(random.uniform(0.1,1),2)
		new_task = Task(random_position[0],random_position[1],risc)
		self.scenario.tasks.append(new_task)

		self.scenario.map[random_position[0],random_position[1]] =\
			self.scenario.tasks[-1].p

	def uniform_sim_sample(self,n_spawns,n_pulverised):
		# 1. Defining the base simulation
		base_sim = self.copy()
		observation = base_sim.get_observation()

		# 2. Removing unseen tasks
		task2remove = list()
		for t in base_sim.scenario.tasks:
			if t.position not in observation:
			  	task2remove.append(t)

		for t in task2remove:
			base_sim.scenario.tasks.remove(t)

		# 3. Sampling tasks
		for i in range(n_spawns-len(observation)-n_pulverised):
			rand_pos = base_sim.agent.position
			while base_sim.agent.vision.in_angle(\
			  base_sim.agent.position,base_sim.agent.direction,rand_pos) and\
			  base_sim.agent.vision.in_radius(\
			  base_sim.agent.position,rand_pos):
				rand_pos = base_sim.scenario.get_random_position()

			new_task = Task(rand_pos[0],rand_pos[1],random.uniform(0.1,1))
			base_sim.scenario.tasks.append(new_task)
			base_sim.scenario.map[rand_pos[0],rand_pos[1]] = new_task.p

		base_sim.update()
		return base_sim

	def n_visible_spaces(self):
		n_visible_spaces = 0
		for i in range(self.scenario.width):
			for j in range(self.scenario.height):
				if self.agent.vision.in_radius(self.agent.position,(i,j))\
				and self.agent.vision.in_angle(self.agent.position,self.agent.direction,(i,j)):
					if self.scenario.map[i,j] == 0:
						n_visible_spaces += 1
					else:
						n_visible_spaces += 2
		return n_visible_spaces

	def get_observation(self):
		observation = list()
		for t in self.scenario.tasks:
			if self.agent.vision.in_radius(self.agent.position,t.position)\
			and self.agent.vision.in_angle(self.agent.position,self.agent.direction,t.position):
				observation.append(t.position)
		return observation

	def get_reward(self,x,y):
		for t in self.scenario.tasks:
			if (x,y) == t.position:
				return (5 + (1-t.p))

	def is_there_task_in_position(self, x, y):
		for t in self.scenario.tasks:
			(t_x, t_y) =  t.position
			if t_x == x and t_y == y:
				return True
		return False

	def position_is_empty(self, x, y):
		if self.agent.position == (x,y):
			return False
		for t in self.scenario.tasks:
			(t_x, t_y) =  t.position
			if (t_x, t_y) == (x, y):
				return False
		return True
		
	def update(self):
		self.scenario.map = np.zeros((self.scenario.width,self.scenario.height))

		for t in self.scenario.tasks:
			t.update()
			self.scenario.map[t.position[0],t.position[1]] = t.p

		self.scenario.map[self.agent.position[0],self.agent.position[1]] = 2

	def copy(self):
		scenario = self.scenario.copy()
		agent = self.agent.copy()
		copy_sim = Simulator(scenario,agent)
		return copy_sim

	def show(self):
		for i in range(self.scenario.width):
			for j in range(self.scenario.height):
				if self.scenario.map[i,j] == 2:
					print 'UAV\t',
				elif self.scenario.map[i,j] == -1:
					print '|||\t',
				elif self.scenario.map[i,j] == 0:
					if self.agent.vision.in_radius(self.agent.position,(i,j))\
					and self.agent.vision.in_angle(self.agent.position,self.agent.direction,(i,j)):
						print '   \t',
					else:
						print '...\t',
				else:
					print '{:.2f}'.format(self.scenario.map[i,j]	),'\t',
			print ''