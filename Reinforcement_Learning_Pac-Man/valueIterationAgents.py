# valueIterationAgents.py
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


# valueIterationAgents.py
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

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        while self.iterations > 0:
          newValues = util.Counter()
          for s in self.mdp.getStates():
            actions = self.mdp.getPossibleActions(s)
            QValues = [self.computeQValueFromValues(s, a) for a in actions] 
            newValues[s] = max(QValues) if QValues else 0
          self.values = newValues
          self.iterations -= 1
        return self.values

    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        if self.mdp.isTerminal(state):
          return 0
        Q = 0
        for nextState, prob in self.mdp.getTransitionStatesAndProbs(state, action):
          Q += prob * (self.mdp.getReward(state, action, nextState) + self.discount * self.getValue(nextState))
        return Q

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        if self.mdp.isTerminal(state):
          return None
        actions = self.mdp.getPossibleActions(state)
        QValues = util.Counter()
        for a in actions:
          QValues.update({a: self.computeQValueFromValues(state, a)})
        return QValues.argMax()

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

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
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        while self.iterations > 0:
          for s in self.mdp.getStates():
            if self.iterations == 0:
              break
            actions = self.mdp.getPossibleActions(s)
            QValues = [self.computeQValueFromValues(s, a) for a in actions] 
            self.values[s] = max(QValues) if QValues else 0
            self.iterations -= 1
        return self.values

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

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

    def Predecessors(self):
      predecessors = {}
      for state in self.mdp.getStates():
        predecessors[state] = set()
      for state in self.mdp.getStates():
        for action in self.mdp.getPossibleActions(state):
          for nextState, prob in self.mdp.getTransitionStatesAndProbs(state, action):
            if prob:
              predecessors[nextState].add(state)
      return predecessors

    def diff(self, s):
      actions = self.mdp.getPossibleActions(s)
      QValues = [self.computeQValueFromValues(s, a) for a in actions] 
      maxQ = max(QValues) if QValues else 0
      return abs(self.getValue(s) - maxQ)

    def runValueIteration(self):
      queue = util.PriorityQueue()
      predecessors = self.Predecessors()
      priorities = {}
      for s in self.mdp.getStates():
        if self.mdp.isTerminal(s):
          pass
        queue.update(s, -1 * self.diff(s))
        priorities[s] = -1 * self.diff(s)
      for i in range(0, self.iterations):
        if queue.isEmpty():
          return
        s = queue.pop()
        if not self.mdp.isTerminal(s):
          actions = self.mdp.getPossibleActions(s)
          QValues = [self.computeQValueFromValues(s, a) for a in actions] 
          self.values[s] = max(QValues) if QValues else 0
        for p in predecessors[s]:
          if self.diff(p) > self.theta:
            queue.update(p, -1 * self.diff(p))
            priorities[p] = -1 * self.diff(p)



