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
    self.home_loc = home
    self.curr_loc = home
    self.dirt_loc = dirt
    self.orientation = orientation
    return

  def __str__(self):
    # TODO: modify as needed
    return f"State(turned_on: {self.turned_on}, curr_loc: {self.curr_loc}, dirt_loc: {self.dirt_loc}, orientation: {self.orientation})"

  def __hash__(self):
    # TODO: modify as needed
    return hash(f"{self.turned_on},{self.curr_loc},{self.dirt_loc},{self.orientation}")

  def __eq__(self, o):
    # TODO: modify as needed
    return (
      self.turned_on == o.turned_on
      and self.curr_loc == o.curr_loc
      and self.dirt_loc == o.dirt_loc
      and self.orientation == o.orientation
    )

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
    self.dirts = random.sample(all_positions, nb_dirts)
    # oriental
    self.orientation = random.randint(0,3)

  def get_initial_state(self):
    # TODO: return the initial state of the environment
    return State(False, self.home, self.dirts, self.orientation)

  def get_legal_actions(self, state):
    actions = []
    # TODO: check conditions to avoid useless actions
    if not state.turned_on:
      actions.append("TURN_ON")
    else:
	# should be only possible when agent has returned home
      if state.turned_on and state.curr_loc == self.home:
        actions.append("TURN_OFF")
      # should be only possible if there is dirt in the current position
      if state.curr_loc in state.dirt_loc:
        actions.append("SUCK")
      # should be only possible when next position is inside the grid (avoid bumping in walls)
      if state.orientation == 0 and state.curr_loc[1] < self._height:
        actions.append("GO")
      if state.orientation == 2 and state.curr_loc[1] > 0:
        actions.append("GO")
      if state.orientation == 1 and state.curr_loc[0] < self._width:
        actions.append("GO")
      if state.orientation == 3 and state.curr_loc[0] > 0:
        actions.append("GO")
      actions.append("TURN_LEFT")
      actions.append("TURN_RIGHT")

    return actions

  def dirt_remove(self, cur_loc, dirt_loc):
    new_dirt = []
    for dirt in dirt_loc:
      if dirt != cur_loc:
        new_dirt.append(dirt)
    return new_dirt

  def get_next_state(self, state, action):
    # TODO: add missing actions
    if action == "TURN_ON":
      return State(True, state.curr_loc, state.dirt_loc, state.orientation)
    elif action == "TURN_OFF":
      return State(False, state.curr_loc, state.dirt_loc, state.orientation)
    elif action == "SUCK":
      _dirt_loc = self.dirt_remove(state.curr_loc, state.dirt_loc)
      return State(True, state.curr_loc, _dirt_loc, state.orientation)
    elif action == "GO":
      if state.orientation == 0:
        _curr_loc = (state.curr_loc[0], (state.curr_loc[1] + 1))
        return State(True, _curr_loc, state.dirt_loc, state.orientation)
      elif state.orientation == 2:
        _curr_loc = (state.curr_loc[0], (state.curr_loc[1] - 1))
        return State(True, _curr_loc, state.dirt_loc, state.orientation)
      elif state.orientation == 1:
        _curr_loc = ((state.curr_loc[0] + 1), state.curr_loc[1])
        return State(True, _curr_loc, state.dirt_loc, state.orientation)
      else:
        _curr_loc = ((state.curr_loc[0] - 1), state.curr_loc[1])
        return State(True, _curr_loc, state.dirt_loc, state.orientation)
    elif action == "TURN_LEFT":
      if state.orientation == 0:
        state.orientation = 3
        return State(True, state.curr_loc, state.dirt_loc, state.orientation)
      else:
        state.orientation -= 1
        return State(True, state.curr_loc, state.dirt_loc, state.orientation)
    elif action == "TURN_RIGHT":
      if state.orientation == 3:
        state.orientation = 0
        return State(True, state.curr_loc, state.dirt_loc, state.orientation)
      else:
        state.orientation += 1
        return State(True, state.curr_loc, state.dirt_loc, state.orientation)
    else:
      raise Exception("Unknown action %s" % str(action))

  def get_cost(self, state, action):
    # TODO: return correct cost of each action
    cost = 0
    def amount_of_dirt_left(): # TODO
      return 5
    at_home_cell = True # TODO

    if action == "TURN_ON":
      cost = 1
    elif action == "TURN_OFF":
      if at_home_cell:
        cost = 1 + (50 * amount_of_dirt_left())
      else:
        cost = 1 + (100 * amount_of_dirt_left())
    elif action == "SUCK": # TODO: implement is_dirt_at_curr_loc function?
      if "DIRT" in state.dirt_loc:
        cost = 1
      else:
        cost = 5
    elif action == "GO": # The Action is Go
      # if "GO" in self.get_legal_actions():
      cost = 1
    elif action == "TURN_LEFT" or action == "TURN_RIGHT":
      cost = 1

    return cost

  def is_goal_state(self, state):
    # TODO: correctly implement the goal test
    if state.curr_loc == self.home and state.dirt_loc == [] and not state.turned_on:
        return True
    else:
        return False

##############

def expected_number_of_states(width, height, nb_dirts):
  # TODO: return a reasonable upper bound on number of possible states
  # The number of expected states is goverend by the size of the grid, W x H, the number of dirts spaces,
  # the agents position, its orientation and if it is turned on or not.

  num_of_states = 4 * 2 * pow((width * height), 2)
  return num_of_states