import datetime
import os
import sys
from random import randint

def create_logs_file(map_num = '0'):
	# 1. Creating a folder for the experiments
	# with the specified map
	path = create_output_folder(map_num)

	# 2. Creating the log file
	# a. getting the experiment time
	now = datetime.datetime.now()

	# b. defining the log key
	key = str(now.day) + "_"+ str(now.hour)+ "_" + str(now.minute)\
	+ "-" + str(randint(0,now.day+now.hour+now.minute))

	# c. opening the log file
	log_file = open(path+key+'log','w')
	result_file = open(path+key+'result','w')

	return log_file,result_file


def create_output_folder(map_num):
	# 1. Verifing the current folder
	current_folder = "outputs/map" + map_num + '/'

	# 2. If the folder doesn't exist, create it
	if not os.path.exists(current_folder):
		os.mkdir(current_folder, 0755)

	# 3. Returning the folder's path
	return current_folder

def show_scenario(log_file,scenario):
	line = ''
	for i in range(scenario.width):
			for j in range(scenario.height):
				line += str(scenario.map[i,j])+'\t'
			line += '\n'
	log_file.write(line)

def show_uav(log_file,uav):
	log_file.write('UAV Parameters\n')
	log_file.write('| position = '+str(uav.position)+'\n')
	log_file.write('| direction = '+str(uav.direction)+'\n')
	log_file.write('| vision radius = '+str(uav.vision.radius)+'\n')
	log_file.write('| vision angle = '+str(uav.vision.angle)+'\n')
	log_file.write('| history = '+str(uav.history)+'\n')

def show_simulator(log_file,simulator):
		for i in range(simulator.scenario.width):
			for j in range(simulator.scenario.height):
				if simulator.scenario.map[i,j] == 2:
					log_file.write('UAV\t') 
				elif simulator.scenario.map[i,j] == -1:
					log_file.write('|||\t') 
				elif simulator.scenario.map[i,j] == 0:
					if simulator.agent.vision.in_radius(simulator.agent.position,(i,j))\
					and simulator.agent.vision.in_angle(simulator.agent.position,simulator.agent.direction,(i,j)):
						log_file.write('   \t') 
					else:
						log_file.write('...\t') 
				else:
					log_file.write('{:.2f}'.format(simulator.scenario.map[i,j])+'\t') 
			log_file.write('\n')

def show_q_table(log_file,node):
    log_file.write('**** Q TABLE ****\n')
    for row in node.Q_table:
        log_file.write(str(node.action)+'\t'+str(row.QValue)+'\t'+str(row.trials)+'\n')
    log_file.write('*****************\n')