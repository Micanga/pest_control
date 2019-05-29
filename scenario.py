import numpy as np
import random

from task import Task

class Scenario:

	def __init__(self,map_num = None):
		self.width = None
		self.height = None
		self.map = None
		self.delay = None
		self.tasks = list()

		if map_num is None:
			self.load_random_scenario('./maps/')
		else:
			self.map_num = map_num
			self.load_scenario('./maps/'+map_num+'.csv')

	def load_random_scenario(self,path):
		scenario_number = str(random.randint(0,0))
		self.map_num = scenario_number
		with open(path+scenario_number+'.csv') as scenario_file:
			for line in scenario_file:
				#print line
				if not self.is_comment(line):
					data = line.strip().split(',')
					key, val = data[0], data[1:]

					if key == 'dimension':
						self.width = int(val[0])
						self.height = int(val[1])
						self.map = np.zeros((self.width,self.height))


					elif key == 'delay':
						self.delay = int(val[0])

	def load_scenario(self,path):
		with open(path) as scenario_file:
			for line in scenario_file:
				if not self.is_comment(line):
					data = line.strip().split(',')
					key, val = data[0], data[1:]

					if key == 'dimension':
						self.width = int(val[0])
						self.height = int(val[1])
						self.map = np.zeros((self.width,self.height))


					elif key == 'delay':
						self.delay = int(val[0])


	@staticmethod
	def is_comment(string):
		for pos in range(len(string)):
			if string[pos] == ' ' or string[pos] == '\t':
				continue
			if string[pos] == '#':
				return True
			else:
				return False

	def get_random_position(self):
		available_positions = self.get_available_positions()
		return random.sample(available_positions,1)[0]

	def get_available_positions(self):
		available_positions = list()

		for i in range(self.width):
			for j in range(self.height):
				if self.map[i,j] == 0:
					available_positions.append((i,j))

		return available_positions

	def copy(self):
		new_scenario = Scenario(self.map_num)
		for i in range(self.width):
			for j in range(self.height):
				new_scenario.map[i,j] = self.map[i,j]
		for t in self.tasks:
			new_task = t.copy()
			new_scenario.tasks.append(new_task)
		return new_scenario

	def show(self):
		for i in range(self.width):
			for j in range(self.height):
				print self.map[i,j],'\t',
			print ''