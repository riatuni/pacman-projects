# value_iteration_agents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# value_iteration_agents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learning_agents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learning_agents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount=0.9, iterations=100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.get_states()
              mdp.get_possible_actions(state)
              mdp.get_transition_states_and_probs(state, action)
              mdp.get_reward(state, action, next_state)
              mdp.is_terminal(state)
        """
        super().__init__()
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.run_value_iteration()
    
    def run_value_iteration(self):
        """
          Run the value iteration algorithm. Note that in standard
          value iteration, V_k+1(...) depends on V_k(...)'s.
        """
        
        states = self.mdp.get_states()

        for iteration in range(self.iterations):
            next_values = util.Counter()

            for state in states:
                if self.mdp.is_terminal(state):
                    continue

                #Markov decision process
                actions = self.mdp.get_possible_actions(state)

                #RAn out of actions
                if not actions:
                    continue

                #V_k+1 = max(sumatory of [probability * reward (for all possible actions)])
                next_values[state] = max(
                    sum(
                        probability * (self.mdp.get_reward(state, action, next_state) + self.discount * self.values[next_state]) for next_state, probability in self.mdp.get_transition_states_and_probs(state, action)
                    ) for action in actions)
            self.values = next_values

            
    def get_value(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]

    def compute_q_value_from_values(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"

        total = 0
        # get possible transitions
        transitions = self.mdp.get_transition_states_and_probs(state, action)
        # for each possible state get the probability of reaching it
        for next_state, probability in transitions:
            reward = self.mdp.get_reward(state, action, next_state)
            future_val = self.values[next_state]
            #add the reward to the future value and multiply by the probability
            total += probability *(reward + self.discount * future_val)
        # return total
        return total
        #util.raise_not_defined()

    def compute_action_from_values(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        # if its a terminal state return none
        if self.mdp.is_terminal(state):
            return None

        # if there are no possible actions return none
        actions = self.mdp.get_possible_actions(state)
        if not actions:
            return None

        # otherwise return the action with wighest value
        best_action = None
        best_value = float('-inf')

        for action in actions:
            q_value = self.compute_q_value_from_values(state, action)
            if q_value > best_value:
                best_value = q_value
                best_action = action

        return best_action
        
        #util.raise_not_defined()

    def get_policy(self, state):
        return self.compute_action_from_values(state)

    def get_action(self, state):
        """Returns the policy at the state (no exploration)."""
        return self.compute_action_from_values(state)

    def get_q_value(self, state, action):
        return self.compute_q_value_from_values(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learning_agents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.get_states()
              mdp.get_possible_actions(state)
              mdp.get_transition_states_and_probs(state, action)
              mdp.get_reward(state)
              mdp.is_terminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def run_value_iteration(self):
        """*** YOUR CODE HERE ***"""
        states = self.mdp.get_states()

        # for all iterations given
        for i in range(self.iterations):
            # get the specific state
            state = states[i % len(states)]
            
            # check if it is a terminal state
            if self.mdp.is_terminal(state): continue

            # get actions
            actions = self.mdp.get_possible_actions(state)
            
            # calculate the new values (given the max q value action)
            self.values[state] = max(
                self.compute_q_value_from_values(state, action) 
                for action in actions
            )



class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learning_agents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def run_value_iteration(self):
        """*** YOUR CODE HERE ***"""
