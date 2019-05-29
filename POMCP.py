from copy import deepcopy
from copy import copy
from math import *
import numpy as np
from numpy.random import choice
from random import sample
import random

import agent
from state import State

actions = ['N', 'S', 'L', 'W', 'P']

########################################################################################################################
class Q_table_row:

    def __init__(self, action, QValue, sumValue, trials):
        self.action = action
        self.QValue = QValue
        self.sumValue = sumValue
        self.trials = trials

########################################################################################################################
class PONode:

    def __init__(self, depth, state, parent=None):

        self.depth = depth
        self.state = state
        self.parent = parent

        self.untried_moves = self.create_possible_moves()
        self.Q_table = self.create_empty_table()

        self.children = list()
        self.action = None

        self.visits = 0

        self.observation = None
        self.history = list()

    def create_empty_table(self):
        Qt = list()

        Qt.append(Q_table_row('N', 0, 0, 0)\
         if 'N' in self.untried_moves else Q_table_row('N', -99999, -99999, 99999))
        Qt.append(Q_table_row('E', 0, 0, 0)\
         if 'E' in self.untried_moves else Q_table_row('E', -99999, -99999, 99999))
        Qt.append(Q_table_row('S', 0, 0, 0)\
         if 'S' in self.untried_moves else Q_table_row('S', -99999, -99999, 99999))
        Qt.append(Q_table_row('W', 0, 0, 0)\
         if 'W' in self.untried_moves else Q_table_row('W', -99999, -99999, 99999))
        Qt.append(Q_table_row('P', 0, 0, 0)\
         if 'P' in self.untried_moves else Q_table_row('P', -99999, -99999, 99999))
        return Qt

    def create_possible_moves(self):
        # 1. Initialising the variables
        (x, y) = self.state.simulator.agent.position
        direction = self.state.simulator.agent.direction

        m = self.state.simulator.scenario.width
        n = self.state.simulator.scenario.height

        untried_moves = ['N', 'E', 'S', 'W','P']

        # 2. Checking which moves are possible
        if x == 0:
            untried_moves.remove('W')

        if y == 0:
            untried_moves.remove('S')

        if x == m - 1:
            untried_moves.remove('E')

        if y == n - 1:
            untried_moves.remove('N')

        return untried_moves

    def random_policy_action(self):
        possible_actions = list()
        for c in self.children:
            possible_actions.append(c.action)
        return choice(possible_actions)

    def get_child_by_action(self,action):
        for c in self.children:
            if c.action == action:
                return c
        return None

    def add_child(self, state, enemy):
        n = PONode(parent=self, depth=self.depth + 1, state=state,enemy=enemy)
        n.history = self.history
        self.children.append(n)
        return n

    def add_action_child(self, act, state):
        new_node = PONode(parent=self, depth=self.depth + 1, state=state)
        new_node.action = act
        new_node.history = copy(self.history)
        new_node.history.append(act)
        self.children.append(new_node)
        return new_node

    def add_obs_child(self, obs, state):
        new_node = PONode(parent=self, depth=self.depth + 1, state=state)
        new_node.observation = obs
        new_node.history = copy(self.history)
        self.children.append(new_node)
        return new_node

    def update(self, action, result):

        # TODO: We should change the table to a dictionary, so that we don't have to find the action
        for i in range(len(self.Q_table)):
            if self.Q_table[i].action == action:
                self.Q_table[i].trials += 1
                self.Q_table[i].sumValue += result
                self.Q_table[i].QValue = self.Q_table[i].sumValue / self.Q_table[i].trials
                return

    def update_depth(self,depth):
        self.depth = depth
        for c in self.children:
            c.update_depth(depth+1)

    def show_q_table(self):
        print '**** Q TABLE ****'
        for row in self.Q_table:
            print row.action,row.QValue,row.trials
        print '*****************'

    def destroy(self):
        for c in self.children:
            c.destroy()

        self.children = None
        self.Q_table = None
        self.untried_moves = None
        self.observation = None

########################################################################################################################
class POMCP:
    def __init__(self,  iteration_max=150, max_depth=30):

        self.root = None
        
        self.iteration_max = iteration_max
        self.max_depth = max_depth

        self.belief_state = list()
        self.k = 250
        self.max_samples = 750
    
    def planning(self, main_time_step, search_tree, sim):
        # 1. Searching for best ad hoc agent movement (+add to history)
        # and the root of POMCP
        next_move, search_tree = self.monte_carlo_planning(main_time_step,search_tree,sim)

        # 2. Returning the result
        return next_move, search_tree

    def monte_carlo_planning(self, main_time_step, search_tree, simulator):
        # 1. Initializing the current state
        sim = simulator.copy()
        current_state = State(sim)

        # 2. Initializing the root
        if search_tree is None:
            #print '> new root'
            self.root = PONode(depth=0, state=current_state)
        else:
            #print '> updating root'
            search_tree.state = current_state
            self.root = search_tree

        # 3. Taking the best action
        #print '- Searching for best action'
        #import ipdb; ipdb.set_trace()
        best_selected_action = self.search(main_time_step, self.root)

        # 5. Retuning the best action and the tree search root
        return best_selected_action, self.root

    def search(self, main_time_step, node):
        sim = node.state.simulator

        # 1. Starting the search main loop
        #print '-- simulating actions'
        it = 0
        # a. choosing the simulation state
        if node.history == list() or self.belief_state == list():
            #print '--- uniform sampling'
            while it < self.iteration_max:
                #if it % 10 == 0:
                    #print it,'/',self.iteration_max
                
                n_spawns = int(main_time_step/sim.scenario.delay)+1
                n_pulverised = sim.agent.n_pulverised
                state = State(sim.uniform_sim_sample(n_spawns,n_pulverised))
                self.belief_state.append(state)

                # b. simulating
                #if it % 50 == 0:
                #    import ipdb; ipdb.set_trace()
                node.state = state
                self.simulate(node,0)

                # c. increasing the time step
                it += 1
        else:
            #print '--- random belief state sampling'
            while it < self.iteration_max:
                #if it % 10 == 0:
                    #print it,'/',self.iteration_max
                
                state = self.belief_state[random.randint(0,len(self.belief_state)-1)]

                # b. simulating
                node.state = state
                self.simulate(node,0)

                # c. increasing the time step
                it += 1

        #print '-- evaluating the simulations'
        return self.best_action(node)

    def simulate(self,node,depth):
        # 0. Setting Simulate Parameters
        state = node.state
        history = node.history

        # 1. Checking the stop condition
        if depth > self.max_depth:
            return 0

        # 2. Searching for the history in childs
        if node.children == []:
            for a in node.create_possible_moves():
                (next_state, observation, reward) = self.simulate_action(state, a)
                node.add_action_child(a,next_state)
            # b. rollout
            return self.rollout(node,depth)

        ##print 'simulate(',depth,')'
        # 3. If the history exists in the tree, choose the best action to simulate
        action, action_idx = self.get_simulate_action(node)
        action_node = node.get_child_by_action(action)

        # 4. Simulate the action
        action_node.visits += 1
        (next_state, observation, reward) = self.simulate_action(state, action)

        # 5. Adding the observation node if it not exists
        new_observation = True
        for child in action_node.children:
            if self.observation_is_equal(child.observation,observation):  
                new_observation = False
                observation_node = child
                break

        if new_observation:
            observation_node = action_node.add_obs_child(observation,next_state)
        
        # 6. Calculating the reward
        observation_node.visits += 1
        R = reward + 0.8*self.simulate(observation_node,depth+1)

        # 7. Updating the node
        if depth == 0:
            self.belief_state.append(state)
        node.visits += 1

        value = node.Q_table[action_idx].QValue
        new_value = value + ((R-value)/action_node.visits)
        node.update(action,new_value)

        return R

    def rollout(self,node,depth):
        ##print 'rollouting (',depth,')...'
        if depth > self.max_depth:
            return 0

        # 1. Choosing the action
        # a ~ pi(h)
        action = node.random_policy_action()

        # 2. Simulating the particle
        # (s',o,r) ~ G(s,a)
        (next_state, observation, reward) = self.simulate_action(node.state, action)

        # 3. Building the rollout node
        new_node = PONode(node.depth+1, next_state)
        for a in new_node.create_possible_moves():
            (c_next_state, c_observation, c_reward) = self.simulate_action(new_node.state, a)
            new_node.add_action_child(a,c_next_state)

        # 4. Calculating the reward
        R = reward + 0.8*self.rollout(new_node,depth+1)

        return R

    ################################################################################################################
    def leaf(self, main_time_step, node):
        if node.depth == main_time_step + self.max_depth + 1:
            return True
        return False

    def best_action(self, node):
        # 1. Getting the node Q-table
        Q_table = node.Q_table
        tieCases = []

        # 2. Choosing the best action
        maxA = None
        maxQ = -100000000000
        for a in range(len(Q_table)):
            if Q_table[a].QValue > maxQ and Q_table[a].trials > 0:
                maxQ = Q_table[a].QValue
                maxA = Q_table[a].action

        # 3. Verifying tie cases
        for a in range(len(Q_table)):
            if (Q_table[a].QValue == maxQ):
                tieCases.append(a)

        # 4. If exist tie cases, pick ramdomly 
        if len(tieCases) > 0:
            maxA = Q_table[choice(tieCases)].action

        return maxA

    def get_simulate_action(self,node):
        action, action_idx = None, None
        actions_value = []
        for a in range(len(node.Q_table)):
            # 1. getting the child node information 
            child = node.get_child_by_action(node.Q_table[a].action)

            # -- if the node was never tried, lets try it
            if child is not None:
                if child.visits == 0:
                    action_idx = a
                    action = node.Q_table[a].action
                    return action, action_idx

                # 2. calculating the value
                value = node.Q_table[a].QValue + sqrt(log(node.visits)/child.visits)
                actions_value.append((value,a))

        # 3. taking the action and the linked child
        action_idx = max(actions_value,key=lambda item:item[0])[1]
        action = node.Q_table[action_idx].action

        return action, action_idx

    def simulate_action(self, state, action):
        # 1. Copying the current simulation state
        sim = state.simulator.copy()

        # 2. Run the M agent simulation
        m_reward, next_sim = self.do_move(sim, action)
        next_state = State(next_sim)

        # 3. Calculating the total reward and taking the observation
        total_reward = float(m_reward)
        observation = next_state.simulator.get_observation()

        return next_state, observation, total_reward

    def is_agent_face_to_item(self,agent,sim):
        dx = [-1, 0, 1,  0]  # 0:W ,  1:N , 2:E  3:S
        dy = [ 0, 1, 0, -1]

        x_diff = 0
        y_diff = 0

        (x, y) = agent.position

        if agent.direction == 2 * np.pi / 2:
            # Agent face to West
            x_diff = dx[0]
            y_diff = dy[0]

        if agent.direction == np.pi / 2:
            # Agent face to North
            x_diff = dx[1]
            y_diff = dy[1]

        if agent.direction == 0 * np.pi / 2:
            # Agent face to East
            x_diff = dx[2]
            y_diff = dy[2]

        if agent.direction == 3 * np.pi / 2:
            # Agent face to South
            x_diff = dx[3]
            y_diff = dy[3]

        if 0 <= x + x_diff < sim.scenario.width and 0 <= y + y_diff < sim.scenario.height\
         and sim.is_there_task_in_position(x + x_diff, y + y_diff) is True:
            return (x + x_diff, y + y_diff)

        return (None,None)

    def do_move(self, sim, move):
        tmp_m_agent = sim.agent.copy()
        previous_vis = sim.n_visible_spaces()
        tmp_m_agent.history.append(move)
        get_reward = 0

        if move == 'P':
            (task_posx, task_posy) = self.is_agent_face_to_item(tmp_m_agent,sim)
            if task_posx is not None and task_posy is not None:
                get_reward = sim.get_reward(task_posx,task_posy)
                
                tmp_m_agent.n_pulverised += 1
                task2remove = list()
                for t in sim.scenario.tasks:
                    if task_posx == t.position[0] and\
                    task_posy == t.position[1]:
                        task2remove.append(t)

                for t in task2remove:
                    sim.scenario.tasks.remove(t)

                sim.scenario.map[task_posx,task_posy] = 0
            else:
                get_reward = - 1

            sim.agent = tmp_m_agent
            sim.update()
        else:
            (x_new, y_new) = self.new_position_with_given_action(tmp_m_agent,\
                sim.scenario.width,sim.scenario.height, move)

            # If there new position is empty
            if sim.position_is_empty(x_new, y_new):
                tmp_m_agent.change_position_direction(sim.scenario.width, sim.scenario.height,move)
            else:
                tmp_m_agent.change_direction_with_action(move)

            sim.agent = tmp_m_agent
            sim.update()

            get_reward = 0.001*(sim.n_visible_spaces()-previous_vis)
    
        return get_reward, sim    

    def new_position_with_given_action(self, agent, dim_w, dim_h, action):

        dx = [-1, 0, 1,  0]  # 0:W ,  1:N , 2:E  3:S
        dy = [0, 1, 0, -1]

        x_diff = 0
        y_diff = 0

        new_position = agent.position
        if action == 'W':
            x_diff = dx[0]
            y_diff = dy[0]
            agent.direction = 2 * np.pi / 2

        if action == 'N':
            x_diff = dx[1]
            y_diff = dy[1]
            agent.direction = np.pi / 2

        if action == 'E':
            x_diff = dx[2]
            y_diff = dy[2]
            agent.direction = 0 * np.pi / 2

        if action == 'S':
            x_diff = dx[3]
            y_diff = dy[3]
            agent.direction = 3 * np.pi / 2

        x, y = agent.position

        if 0 <= x + x_diff < dim_w and 0 <= y + y_diff < dim_h:
            new_position = (x + x_diff, y + y_diff)

        return new_position

    ################################################################################################################
    def update_belief_state(self,main_t,main_sim,prev_sim,search_tree):
        # 1. Taking the real action and the real observation
        action = main_sim.agent.history[-1]
        observation = main_sim.get_observation()

        # 2. Walking on the tree
        # a. root --- go to ---> action node
        #print '- Searching for the new child node'
        for action_child in search_tree.children:
            if action == action_child.action:
                search_tree = action_child
                break
        search_tree.parent = None

        # b. action node --- go to ---> observation node
        #print '- Validating the observation'
        for obs_child in search_tree.children:
            ##print 'c',obs_child.observation
            if self.observation_is_equal(observation,obs_child.observation) and\
            obs_child.state.simulator.agent.position == main_sim.agent.position:
                search_tree = obs_child
                break
        search_tree.parent = None

        # #print '********* Updating the belief state **********'
        if search_tree.observation == None:
            state = State(search_tree.state.simulator.copy())
            history = copy(search_tree.history)

            search_tree.destroy()

            search_tree = PONode(parent=None, depth=0, state=state)
            search_tree.observation = observation
            search_tree.history = history

        #print '- Running a black_box'
        self.black_box(action,observation,prev_sim)

        # #print '********* Updating the tree depth **********'
        search_tree.update_depth(0)

        # #print 'new root:',search_tree,'depth:',search_tree.depth,'history:',search_tree.history

        return search_tree

    def black_box(self,action,real_obs,prev_sim):
        # 1. Copying and cleaning the current belief states
        cur_belief = list()

        #print '-- filtering the belief states'
        for state in self.belief_state:
            (next_state, observation, reward) = self.simulate_action(state, action)
            if self.observation_is_equal(observation,real_obs):
                cur_belief.append(state)

        #print '--- Survived Particles:',len(cur_belief)
        #print '--- Removed Particles:',len(self.belief_state)-len(cur_belief)
        self.belief_state = list()

        # 2. Sampling new particles while dont get k particles
        #print '-- sampling new states to fill the belief filter'
        added_particles = 0
        sample_counter = 0
        if len(cur_belief) > 0: 
            while added_particles < self.k and sample_counter < self.max_samples:
                sample_counter += 1

                if len(cur_belief) == 1:
                    state = cur_belief[0]
                else:
                    state = sample(cur_belief,1)[0]

                (next_state, observation, reward) = self.simulate_action(state, action)
                if self.observation_is_equal(real_obs,observation):
                    added_particles += 1
                    self.belief_state.append(next_state)

    def observation_is_equal(self,observation,other_observation):
        if len(observation) != len(other_observation):
            return False

        for o in range(len(observation)):
            if observation[o] not in other_observation:
                return False

        return True
