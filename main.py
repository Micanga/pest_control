from copy import copy
from math import pi, sqrt
import random
import sys

from agent import Agent
from scenario import Scenario
from state import State
from simulator import Simulator
import log

# LOG INITIALIZATION
EXPLORATION_ROUNDS = list()
PULVERIZATION_ROUNDS = list()
PLAGUE_LIST = list()

# 1. Initializing the scenario
if len(sys.argv) == 1:
	scenario = Scenario()
	log_file,result_file = log.create_logs_file()
else:
	scenario = Scenario(sys.argv[1])
	log_file,result_file = log.create_logs_file(sys.argv[1])
#print 'Loaded Scenario'
log_file.write('Loaded Scenario\n')
#scenario.show()
log.show_scenario(log_file,scenario)

# 2. Initializing the agent
position = scenario.get_random_position()
direction = random.sample(['N','S','W','E'],1)[0]
radius = int(sqrt(scenario.width*scenario.height)*0.5)
angle = 2*pi

uav = Agent(position[0],position[1],direction,radius,angle)
#uav.show()
log.show_uav(log_file,uav)

# 3. Defining simulation parameter
max_time = 200
stop_spawn = 0.75*max_time
simulator = Simulator(scenario,uav)
#print 'Simulation Created'
log_file.write('Simulation Created\n')

search_tree = None

# 4. Starting the simulation
simulator.spawn_task()
for t in range(1,max_time):
	if len(simulator.get_observation()) == 0:
		EXPLORATION_ROUNDS.append(1)
		PULVERIZATION_ROUNDS.append(0)
	else:
		EXPLORATION_ROUNDS.append(0)
		PULVERIZATION_ROUNDS.append(1)

	PLAGUE_LIST.append([task.p for task in simulator.scenario.tasks])

	#print 'Simulation at time',t
	log_file.write('Simulation at time '+str(t)+'\n')
	#simulator.show()
	log.show_simulator(log_file,simulator)
	#print 'Eliminations: ',simulator.agent.n_pulverised
	log_file.write('Eliminations: '+str(simulator.agent.n_pulverised)+'\n')

	# a. spawning a task
	if t % scenario.delay == 0 and t < stop_spawn:
		#print 'Spawning new tasks'
		log_file.write('Spawning new tasks\n')
		simulator.spawn_task()
	elif t >= stop_spawn and len(simulator.scenario.tasks) == 0:
		#print '===== SIMULATION FINISHED'
		log_file.write('===== SIMULATION FINISHED\n')
		break;

	# b. agent planning
	#print 'Agent route planning'
	log_file.write('Agent route planning\n')
	next_move, search_tree = simulator.agent.pomcp.planning(t,search_tree, simulator)
	#print 'Best move',next_move
	log_file.write('Best move'+str(next_move)+'\n')
    #search_tree.show_q_table()
	log.show_q_table(log_file,search_tree)

	# c. moving the agent
	#print 'Agent performing movement (',next_move,')'
	log_file.write('Agent performing movement ('+str(next_move)+')\n')
	previous_simulator = simulator.copy()
	r, simulator = simulator.agent.pomcp.do_move(simulator,next_move)
	#print '- History: ',simulator.agent.history
	log_file.write('- History: '+str(simulator.agent.history)+'\n')
	#print '- Observation: ',simulator.get_observation()
	log_file.write('- Observation: '+str(simulator.get_observation())+'\n')

	# d. updating the search tree
	#print 'Updating the knowledge'
	log_file.write('Updating the knowledge\n')
	search_tree = simulator.agent.pomcp.\
		update_belief_state(t,simulator,previous_simulator,search_tree)
	
	if len(simulator.agent.pomcp.belief_state) > 0:
		current_belief_state = copy((random.sample(simulator.\
			agent.pomcp.belief_state,1)[0]).simulator)
	else:
		current_belief_state = None

	# d. updating simulation
	simulator.update()

# 5. Writing the results
result_file.write('Total Rounds: '+str(t)+'/'+str(max_time)+'\n')
result_file.write('Exploration Rounds: '+str(EXPLORATION_ROUNDS)+'\n')
result_file.write('Pulverization Rounds: '+str(PULVERIZATION_ROUNDS)+'\n')
result_file.write('Plague List: '+str(PLAGUE_LIST)+'\n')

# 6. Closing the opened files
log_file.close()
result_file.close()