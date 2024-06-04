import collections
from queue import PriorityQueue
######################

class Heuristics:

	env = None

	# inform the heuristics about the environment, needs to be called before the first call to eval()
	def init(self, env):
		self.env = env

	# return an estimate of the remaining cost of reaching a goal state from state s
	def eval(self, s):
		raise NotImplementedError()

######################

class SimpleHeuristics(Heuristics):

	def eval(self, s):
		h = 0
		# if there is dirt: max of { manhattan distance to dirt + manhattan distance from dirt to home }
		# else manhattan distance to home
		if len(s.dirts) == 0:
			h = self.nb_steps(s.position, self.env.home)
		else:
			for d in s.dirts:
				steps = self.nb_steps(s.position, d) + self.nb_steps(d, self.env.home)
				if (steps > h):
					h = steps
			h += len(s.dirts) # sucking up all the dirt
		if s.turned_on:
			h += 1 # to turn off
		return h

	 # estimates the number of steps between locations a and b by Manhattan distance
	def nb_steps(self, a, b):
		return abs(a[0] - b[0]) + abs(a[1] - b[1])

######################

class SearchAlgorithm:
	heuristics = None

	def __init__(self, heuristics):
		self.heuristics = heuristics

	# searches for a goal state in the given environment, starting in the current state of the environment,
	# stores the resulting plan and keeps track of nb. of node expansions, max. size of the frontier and cost of best solution found
	def do_search(self, env):
		raise NotImplementedError()

	# returns the plan found, the last time do_search() was executed
	def get_plan(self):
		raise NotImplementedError()

	# returns the number of node expansions of the last search that was executed
	def get_nb_node_expansions(self):
		raise NotImplementedError()

	# returns the maximal size of the frontier of the last search that was executed
	def get_max_frontier_size(self):
		raise NotImplementedError()

	# returns the cost of the plan that was found
	def get_plan_cost(self):
		raise NotImplementedError()

######################

# A Node is a tuple of these four items:
#  - value: the evaluation of this node
#  - parent: the parent of the node, or None in case of the root node
#  - state: the state belonging to this node
#  - action: the action that was executed to get to this node (or None in case of the root node)

Node = collections.namedtuple('Node',['value', 'parent', 'state', 'action'])

######################

class AStarSearch(SearchAlgorithm):
	nb_node_expansions = 0
	max_frontier_size = 0
	goal_node = None

	def __init__(self, heuristic):
		super().__init__(heuristic)

	def do_search(self, env):
		self.heuristics.init(env)
		self.nb_node_expansions = 0
		self.max_frontier_size = 0
		self.goal_node = None

		visited_states = []

		#initialize frontier with starting node
		current_state = env.get_current_state()
		current_heuristic = self.heuristics.eval(current_state)
		start_node = Node(0, None, current_state, None)
		path_cost = []
		frontier2 = PriorityQueue()
		#frontier = []
		#heapq.heappush(frontier, (current_heuristic, start_node))
		item = (current_heuristic, start_node)
		frontier2.put(item)

		# TODO implement the search here
		# Update nb_node_expansions and max_frontier_size while doing the search:
		# - nb_node_expansions should be incremented by one for each node popped from the frontier
		# - max_frontier_size should be the largest size of the frontier observed during the search measured in number of nodes
		# Once a goal node has been found, set the goal_node variable to it, this should take care of get_plan() and get_plan_cost() below,
		# as long as the node contains the right information.

		while len(frontier2.queue) > 0:
			if len(frontier2.queue) > self.max_frontier_size:
				self.max_frontier_size = len(frontier2.queue)

			#priority, current_node = heapq.heappop(frontier)
			priority, current_node = frontier2.get()

			# print("----------Núverandi priority--------")
			# print(priority)
			self.nb_node_expansions += 1
			current_state = current_node.state
			visited_states.append(hash(current_state))
			# print('----------------------VISITED STATES------------------', visited_states)
			path_cost.append(current_node.value)

			# print("Núverandi action: ")
			# print(current_node.action)
			# print("Núverandi staða: ")
			# print(current_state)
			# print("Núverandi node value: ")
			# print(current_node.value)
			# print("---------------------------------------------")
			# print("Finna næsta frontier")
			# print("---------------------------------------------")

			if env.is_goal_state(current_state):
				# print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>     HALELUJAH      -------------------------------------')
				# print('------GOAL: ', current_node)
				self.goal_node = current_node
				break

			#get available actions for current state
			next_actions = env.get_legal_actions(current_state)
			#Get children of current node from available legal actions
			#and add them to the frontier
			for action in next_actions:
				new_state = env.get_next_state(current_state, action)
				#get parents g_value from g(n) = f(n) - h(n)
				g_parent = current_node.value
				#childs g_value is the parents g_value plus the cost of the childs action
				g_child = g_parent + env.get_cost(new_state, action)
				#f(n) = g(n) + h(n)
				f_value = g_child + self.heuristics.eval(new_state)
				child_node = Node(g_child, current_node, new_state, action)

				#TODO
				#if not child_state_in_frontier:
				#frontier.put(f_value, child_node)
				if (f_value, child_node) not in frontier2.queue and hash(new_state) not in visited_states:
				# if hash(child_node.state) not in visited_states:
					new_item = (f_value, child_node)
					frontier2.put(new_item)
					visited_states.append(hash(new_state))
					#heapq.heappush(frontier, (f_value, child_node))

			# print("---------------------Skoða hvað er inni í frontier------------------------")
			# for _, pcb in frontier2.queue:
			# 	print('pq', pcb, '\n')
			#for i in range(len(frontier.queue)):
			#	print(frontier.queue[i])
			# print("---------------------------------------------")

			#setja næstu nóð sem goal til að test-a hvað agent-inn gerir
			self.goal_node = current_node
			# print("stærð á frontier: " + str(len(frontier2.queue)))
			# print("Stöður heimsóttar: " + str(len(visited_states)))
			# print("---------------------------------------------\n\n")
			# print("---------------------------------------------")

		return

	def get_plan(self):
		if not self.goal_node:
			return None

		plan = []
		n = self.goal_node
		while n.parent:
			plan.append(n.action)
			n = n.parent

		return plan[::-1]

	def get_nb_node_expansions(self):
		return self.nb_node_expansions

	def get_max_frontier_size(self):
		return self.max_frontier_size

	def get_plan_cost(self):
		if self.goal_node:
			return self.goal_node.value
		else:
			return 0
