from copy import deepcopy

class State:

    def __init__(self, simulator):
        self.simulator = simulator

    def equals(self, state):
        return self.simulator.equals(state.simulator)

    def copy(self):
    	new_state = State(self.simulator.copy())
    	return new_state
