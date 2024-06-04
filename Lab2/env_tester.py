#!/usr/bin/env python

import argparse
import random
import sys
import time

import pysize

from environment import *

##############

"""returns a list of all reachable states in the environment
"""
def bfs_traverse(env, expected_nb_states):
  state = env.get_initial_state()
  # print("initial state: %s" % (str(state)))
  visited = {state:1}
  open_list = [state]
  while len(open_list)>0:
    if len(visited) > expected_nb_states:
      print("ERROR: generating more states than expected!")
      print("Either identical states are not detected or the expected number is wrong.")
      print("Stopping state generation before all states are found!\n")
      return visited.keys()
    state = open_list.pop()
    if not env.is_goal_state(state):
      for next_state in [env.get_next_state(state, a) for a in env.get_legal_actions(state)]:
        if next_state not in visited:
          visited[next_state] = 1
          open_list.append(next_state)
  return list(visited.keys())

##############

def run_simulation(env, nb_steps):
  state = env.get_initial_state()
  actions = env.get_legal_actions(state)
  if len(actions) == 0:
    print("ERROR: initial state %s has no legal actions" % str(state))
    return
  terminal = False
  step = 0
  path_cost = 0
  while not terminal and step < nb_steps:
    print("Step %d" % step)
    print("  state: %s" % str(state))
    print("  state has %d legal actions: %s" % (len(actions), str(actions)))
    action = random.choice(actions)
    print("  chosen action: %s" % str(action))
    cost = env.get_cost(state, action)
    path_cost += cost
    print("  cost: %s" % str(cost))
    state = env.get_next_state(state, action)
    print("  next state: %s" % str(state))
    if env.is_goal_state(state):
      print("Goal state found! Path cost: %s" % (str(path_cost)))
      terminal = True
    else:
      actions = env.get_legal_actions(state)
      if len(actions) == 0:
        print("Dead end found! (state with no legal actions)")
        terminal = True
    print("")
    step += 1
  return

##############

def main(argv):
  parser = argparse.ArgumentParser(
    description='Generate all states of an environment and check whether they hash correctly.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("-s", "--simulate", metavar='N', type=int, help="run an N step simulation of the environment using random actions instead of generating all states")
  parser.add_argument('width', type=int, nargs='?', default=5, help='width of the grid')
  parser.add_argument('height', type=int, nargs='?', default=5, help='height of the grid')
  parser.add_argument('nb_dirts', type=int, nargs='?', default=5, help='number of dirt spots scattered in the grid')
  args = parser.parse_args()

  width = args.width
  height = args.height
  nb_dirts = args.nb_dirts

  if args.simulate:
    # create environment and simulate it
    print("Creating environment with %dx%d cells and %d dirt spots." % (width, height, nb_dirts))
    env = Environment(width, height, nb_dirts)
    run_simulation(env, args.simulate)
    return

  expected_nb_states = expected_number_of_states(width, height, nb_dirts)

  # create environment and generate all reachable states
  print("Creating environment with %dx%d cells and %d dirt spots. Expecting %d states." % (width, height, nb_dirts, expected_nb_states))
  start_time = time.process_time_ns()
  env = Environment(width,height,nb_dirts)
  states = bfs_traverse(env, expected_nb_states)
  end_time = time.process_time_ns()
  if expected_nb_states < len(states): # not all states were generated
    return
  goal_states = list(filter(lambda x: env.is_goal_state(x), states))
  print("The environment has %d reachable states of which %d are goal states." % (len(states), len(goal_states)))
  if expected_nb_states > len(states): # not all states were generated
    factor_off = expected_nb_states / len(states)
    print("Your estimate is off by a factor of %.2f (Why?)" % factor_off) 
  else:
    print("Your estimate was exactly right!")
  print("Generating those states took: %.2fs (%.0f states/s)" % ((end_time-start_time)/10**9, 10**9*len(states)/(end_time-start_time)))

  # estimate size of states in memory
  size_of_all_states = pysize.get_size(states)
  size_of_initial_state = pysize.get_size(env.get_initial_state())
  size_of_environment = pysize.get_size(env)
  print()
  print("size of environment: %d bytes" % size_of_environment)
  print("size of initial state: %d bytes" % size_of_initial_state)
  print("size of all reachable states: %d bytes (%d bytes/state on average)" % (size_of_all_states, int(size_of_all_states/len(states))))

  # check whether "equal" states are actually comparable (have the same hash and == is True)
  print()
  states2 = bfs_traverse(env, expected_nb_states)
  nb_errors = 0
  if len(states2) != len(states):
    nb_errors += 1
    print("ERROR: reachable state set is not deterministic")
  dict1 = {state:1 for state in states}
  for state in states2:
    if state not in dict1:
      nb_errors += 1
      print("ERROR: state %s can't be found in reachable states set" % str(state))
  if nb_errors == 0:
    print("Great! State's hash and equals functions seem to do the right thing!")

  # check how many hash collisions we get
  print()
  nb_states = len(states)
  hashes = [hash(state) for state in states]
  nb_unique_hashes = len(set(hashes))
  print("%d unique hashes (%.1f%% hash collisions)" % (nb_unique_hashes, 100*(1-nb_unique_hashes/nb_states)))
  # The computation of the hash indices is based on the fact that the size of a dict is a power of 2
  # and is increased to the next power of two, whenever the dict is more 2/3 full.
  # The index computed from the hash value are simply the [bits] least significant bits of the hash value.
  bits = 0
  while 2 ** bits / 1.5 < nb_states:
    bits += 1
  probe_mask = 2 ** bits - 1
  hash_indices = [h & probe_mask for h in hashes]
  nb_unique_hash_indices = len(set(hash_indices))
  print("%d unique hash indizes (%.1f%% index collision)" % (nb_unique_hash_indices, 100*(1-nb_unique_hash_indices/nb_states)))

if __name__ == "__main__":
  main(sys.argv)
