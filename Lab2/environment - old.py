from enum import IntEnum
import random
import itertools

##############

class Orientation(IntEnum):
  NORTH = 0
  EAST = 1
  SOUTH = 2
  WEST = 3

  # this allows things like: Orientation.NORTH + 1 == Orientation.EAST
  def __add__(self, i):
    orientations = list(Orientation)
    return orientations[(int(self) + i) % 4]

  def __sub__(self, i):
    orientations = list(Orientation)
    return orientations[(int(self) - i) % 4]

##############

class State:
  # Note, that you do not necessarily have to use this class if you find a
  # different data structure more useful as state representation.

  # TODO: add other attributes that store necessary information about a state of the environment
  #       Only information that can change over time should be kept here.
  turned_on = False

  def __init__(self, turned_on, home, dirt, orientation):
  # TODO: add other attributes that store necessary information about a state of the environment
    self.turned_on = turned_on
    self.dirt_location = dirt
    self.orientation = orientation
    self.home = home
    self.current_location = home
    return

  def __str__(self):
    # TODO: modify as needed
    return f"State(Turned on: {self.turned_on}, Location: {self.current_location}, " \
           f"Orientation: {self.orientation}, Dirt location: {self.dirt_location})"

  def __hash__(self):
    # TODO: modify as needed
   return 1

  def __eq__(self, o):
    # TODO: modify as needed
    return self is o

##############

class Environment:
  # TODO: add other attributes that store necessary information about the environment
  #       Information that is independent of the state of the environment should be here.
  _width = 0
  _height = 0

  def __init__(self, width, height, nb_dirts):
    self._width = width
    self._height = height
    # TODO: randomly initialize an environment of the given size
    # That is, the starting position, orientation and position of the dirty cells should be (somewhat) random.
    # for example as shown here:
    # generate all possible positions
    all_positions = list(itertools.product(range(1, self._width+1), range(1, self._height+1)))
    # randomly choose a home location
    self.home = random.choice(all_positions)
    # randomly choose locations for dirt
    self.dirt = random.sample(all_positions, nb_dirts)
    # randomly choose starting orientation
    self.orientation = Orientation(random.randint(0, 3))

  def get_initial_state(self):
    # TODO: return the initial state of the environment
    return State(False, self.home, self.dirt, self.orientation)

  def get_legal_actions(self, state):
    actions = []
    # TODO: check conditions to avoid useless actions
    if not state.turned_on:
      actions.append("TURN_ON")
    else:
      # should be only possible when agent has returned home
      if state.turned_on and state.current_location == state.home:
        actions.append("TURN_OFF")
      #should be only possible if there is dirt in the current position
      if state.current_location in state.dirt_location:
        actions.append("SUCK")
      ## should be only possible when next position is inside the grid (avoid bumping in walls)
      if state.orientation == Orientation.NORTH and state.current_location[1] < self._height+1:
        actions.append("GO")
      elif state.orientation == Orientation.SOUTH and state.current_location[1] > 1:
        actions.append("GO")
      elif state.orientation == Orientation.EAST and state.current_location[0] < self._width + 1:
        actions.append("GO")
      elif state.orientation == Orientation.WEST and state.current_location[0] > 1:
        actions.append("GO")
      actions.append("TURN_LEFT")
      actions.append("TURN_RIGHT")
    return actions

  def get_next_state(self, state, action):
    # TODO: add missing actions
    if action == "TURN_ON":
      return State(True, state.current_location, state.dirt_location, state.orientation)
    elif action == "TURN_OFF":
      return State(False, state.current_location, state.dirt_location, state.orientation)
    elif action == "TURN_RIGHT":
      return State(True, state.current_location, state.dirt_location, state.orientation.__add__())
    elif action == "TURN_LEFT":
      return State(True, state.current_location, state.dirt_location, state.orientation.__sub__())
    elif action == "GO":
      if self.orientation == Orientation.NORTH:
        return  State(True, state.current_location[1] + 1, state.dirt_location, state.orientation)
      elif self.orientation == Orientation.SOUTH:
        return State(True, state.current_location[1] - 1, state.dirt_location, state.orientation)
      elif self.orientation == Orientation.EAST:
        return State(True, state.current_location[0] + 1, state.dirt_location, state.orientation)
      else:
        return State(True, state.current_location[0] - 1, state.dirt_location, state.orientation)
    else:
      raise Exception("Unknown action %s" % str(action))

  def get_cost(self, state, action):
    # TODO: return correct cost of each action
    return 1

  def is_goal_state(self, state):
    # TODO: correctly implement the goal test
    #Start by finding dirt as first goal state
    return not state.turned_on

##############

def expected_number_of_states(width, height, nb_dirts):
  # TODO: return a reasonable upper bound on number of possible states
  #The number of expected states is goverend by the size of the grid, the number of dirts spaces,
  #the agents orientation (4 possible states) and if it is turned on or not (2 possible states.
  num_of_states = width*height*nb_dirts*4*2
  return num_of_states
