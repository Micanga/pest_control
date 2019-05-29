from math import exp

class Task:

	def __init__(self,x,y,p):
		self.position = (x,y)
		self.p = p

	def update(self):
		self.p = self.p*1.01 \
			if self.p*1.01 <= 1 else 1

	def copy(self):
		new_task = Task(self.position[0],self.position[1],self.p)
		return new_task