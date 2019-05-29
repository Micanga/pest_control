from copy import deepcopy
import numpy as np

from POMCP import POMCP
import sensor

class Agent: 

	def __init__(self,x,y,direction,radius,angle):
		self.position = (int(x), int(y))

		if isinstance(direction, basestring):
			self.direction = self.convert_direction(direction)
		else:
			self.direction = float(direction)

		self.pomcp = POMCP()

		self.vision = sensor.VisionSensor(radius,angle)

		self.history = list()

		self.n_pulverised = 0

	@staticmethod
	def convert_direction(direction):

		if direction == 'N':
			return np.pi / 2

		if direction == 'W':
			return np.pi

		if direction == 'E':
			return 0

		if direction == 'S':
			return 3*np.pi/2

	def change_position_direction(self, dim_w, dim_h, action):
		dx = [-1, 0, 1,  0]  # 0:W ,  6AGA_O_2:N , 2:E  3:S
		dy = [0, 1, 0, -1]

		x_diff = 0
		y_diff = 0

		if action == 'W':
			x_diff = dx[0]
			y_diff = dy[0]
			self.direction = 2 * np.pi / 2

		if action == 'N':
			x_diff = dx[1]
			y_diff = dy[1]
			self.direction = np.pi / 2

		if action == 'E':
			x_diff = dx[2]
			y_diff = dy[2]
			self.direction = 0 * np.pi / 2

		if action == 'S':
			x_diff = dx[3]
			y_diff = dy[3]
			self.direction = 3 * np.pi / 2

		x, y = self.position

		if 0 <= x + x_diff < dim_w and 0 <= y + y_diff < dim_h:
			self.position = (x + x_diff, y + y_diff)

		return self.position

	def change_direction_with_action(self, action):

		if action == 'W':  # 'W':
			self.direction = 2 * np.pi / 2

		if action == 'N':  # 'N':
			self.direction = np.pi / 2

		if action == 'E':  # 'E':
			self.direction = 0 * np.pi / 2

		if action == 'S':  # 'S':
			self.direction = 3 * np.pi / 2

	def copy(self):
		posx = self.position[0]
		posy = self.position[1]
		direction = self.direction
		radius = self.vision.radius
		angle = self.vision.angle
		new_agent = Agent(posx,posy,direction,radius,angle)
		new_agent.pomcp = self.pomcp
		new_agent.history = [h for h in self.history]
		new_agent.n_pulverised = self.n_pulverised
		return new_agent

	def show(self):
		print 'UAV Parameters'
		print '| position = ',self.position
		print '| direction = ',self.direction
		print '| vision radius = ',self.vision.radius
		print '| vision angle = ',self.vision.angle
		print '| history = ',self.history