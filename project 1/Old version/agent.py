import random
import time
import copy

from environment import *

#############

"""Agent acting in some environment"""


class Agent(object):

    # this method is called on the start of the new environment
    # override it to initialise the agent
    def start(self, role, width, height, play_clock):
        print("start called")
        return

    # this method is called on each time step of the environment
    # it needs to return the action the agent wants to execute as a string
    def next_action(self, last_move):
        print("next_action called")
        return "NOOP"

    # this method is called when the environment has reached a terminal state
    # override it to reset the agentN
    def cleanup(self, last_move):
        print("cleanup called")
        return


#############

"""A random Agent for the KnightThrough game

 RandomAgent sends actions uniformly at random. In particular, it does not check
 whether an action is actually useful or legal in the current state.
 """


class RandomAgent(Agent):
    role = None
    play_clock = None
    my_turn = False
    width = 0
    height = 0

    # start() is called once before you have to select the first action. Use it to initialize the agent.
    # role is either "white" or "black" and play_clock is the number of seconds after which nextAction must return.
    def start(self, role, width, height, play_clock):
        self.play_clock = play_clock
        self.role = role
        self.my_turn = role != 'white'
        # we will flip my_turn on every call to next_action, so we need to start with False in case
        #  our action is the first
        self.width = width
        self.height = height
        # TODO: add your own initialization code here
        return

    def next_action(self, last_action):
        if last_action:
            if self.my_turn and self.role == 'white' or not self.my_turn and self.role != 'white':
                last_player = 'white'
            else:
                last_player = 'black'
            print("%s moved from %s to %s" % (last_player, str(last_action[0:2]), str(last_action[2:4])))
            # TODO: 1. update your internal world model according to the action that was just executed
        else:
            print("first move!")

        # update turn (above that line it myTurn is still for the previous state)
        self.my_turn = not self.my_turn
        if self.my_turn:
            # TODO: 2. run alpha-beta search to determine the best move

            # Here we just construct a random move (that will most likely not even be possible),
            # this needs to be replaced with the actual best move.
            x1 = random.randint(1, self.width)
            x2 = x1 + random.randint(1, 2) * random.choice([-1, 1])
            y1 = random.randint(1, self.height)
            direction = 1
            if self.role == 'black':
                direction = -1
            y2 = y1 + direction * random.randint(1, 2)
            return "(move " + " ".join(map(str, [x1, y1, x2, y2])) + ")"
        else:
            return "noop"

#############

"""A random Agent for the KnightThrough game

 RandomAgent sends actions uniformly at random. In particular, it does not check
 whether an action is actually useful or legal in the current state.
 """


class MyAgent(Agent):
    role = None
    play_clock = None
    my_turn = False
    width = 0
    height = 0

    # start() is called once before you have to select the first action. Use it to initialize the agent.
    # role is either "white" or "black" and play_clock is the number of seconds after which nextAction must return.
    def start(self, role, width, height, play_clock):
        self.play_clock = play_clock
        self.role = role
        self.my_turn = role != 'white'
        # we will flip my_turn on every call to next_action, so we need to start with False in case
        #  our action is the first
        self.width = width
        self.height = height

        # TODO: add your own initialization code here
        self.env = Environment(width, height, (not self.my_turn)) # "not" because we start with False
        return

    def next_action(self, last_action):
        if last_action:
            if self.my_turn and self.role == 'white' or not self.my_turn and self.role != 'white':
                last_player = 'white'
            else:
                last_player = 'black'
            print("%s moved from %s to %s" % (last_player, str(last_action[0:2]), str(last_action[2:4])))
            # TODO: 1. update your internal world model according to the action that was just executed
            moves = [i - 1 for i in list(last_action)]
            self.env.do_move(self.env.current_state, moves) # TODO Er þetta málið? Nóg?
            # print(self.env.current_state)
        else:
            print("first move!")

        # update turn (above that line it myTurn is still for the previous state)
        self.my_turn = not self.my_turn
        if self.my_turn:
            # TODO: 2. run alpha-beta search to determine the best move

            self.expanded = 0
            self.best_move = []
            ''' minimax with alpha_beta pruning '''
            def minimax_ab(state, depth, alpha = -128, beta = 127, maximize = True):
                # if self.elapsed + 0.5 >= self.play_clock:
                #     raise TimeoutError

                if self.env.is_terminal(state) or (depth <= 0):
                # if self.env.is_terminal(state) or (depth <= 0) or (self.elapsed + 0.5 >= self.play_clock):
                    return (self.env.evaluate_state(state)), None

                legal_moves = self.env.get_legal_moves(state)

                # makeshift move order
                def move_order(move):
                    _state = copy.deepcopy(state)
                    return self.env.evaluate_state(self.env.do_move(_state, move)) + depth

                if maximize:
                    max_val = -100
                    best_move = []
                    legal_moves.sort(key=move_order, reverse=True)
                    for move in legal_moves:
                        self.expanded += 1
                        new_state = self.env.do_move(state, move)
                        value, _ = minimax_ab(new_state, depth - 1, alpha, beta, False)
                        self.env.undo_move(state, move)

                        # max_val = max(max_val, value)

                        # print('MAX_VALUE '*6, max_val, value)
                        if max_val < value:
                            max_val = value
                            self.best_move = move
                            best_move = move

                        # ab pruning
                        if max_val > alpha:
                            alpha = max_val
                            if beta <= alpha:
                                break

                    # print(expanded, end=', ')
                    # print('maximizing', max_val)
                    return max_val, best_move

                else: # minimize
                    min_val = 100
                    legal_moves.sort(key=move_order) # NO reverse
                    best_move = []
                    for move in legal_moves:
                        self.expanded += 1
                        new_state = self.env.do_move(state, move)
                        value, _ = minimax_ab(new_state, depth - 1, alpha, beta, True)
                        self.env.undo_move(state, move)

                        min_val = min(min_val, value)
                        if value < min_val:
                            min_val = value
                            self.best_move = move
                            best_move = move

                        # ab pruning
                        if min_val < beta:
                            beta = min_val
                            if beta <= alpha:
                                break

                    # print('MINIMIZING', min_val)
                    return min_val, best_move


            def negamax_alpha_beta(state, depth, alpha = -124, beta = 124, color = 1):
                # self.expanded = 0
                if self.env.is_terminal(state) or depth == 0:
                    #print("Depth == 0 or terminal")
                    #print("Color: ", color)
                    #print("Score: ", self.env.evaluate_state(state))
                    return color * self.env.evaluate_state(state), None

                # makeshift move order
                #def move_order(move):
                #    _state = copy.deepcopy(state)
                #    return self.env.evaluate_state(self.env.do_move(_state, move))

                best_value = -100
                best_move = [4, 4, 4, 4]

                legal_moves = self.env.get_legal_moves(state)
                for move in legal_moves:
                    # legal_moves.sort(key=move_order, reverse=True)
                    self.expanded += 1
                    child_state = self.env.do_move(state, move)
                    value, _ = negamax_alpha_beta(child_state, depth - 1, -alpha, -beta, -color)
                    value = -value
                    # self.env.set_role(self.env.r * - 1) # FIXME: hacky, use separate var
                    self.env.undo_move(state, move)

                    #if minmax > 0:
                    #    print("Negamax value: ", value)
                    #    print("For player: ", minmax)
                    #    print("At depth: ", depth)
                    #    print("Current best value: ", best_value)
                    #best_value = max(best_value, value)
                    if value > best_value:
                        best_value = value
                        best_move = move

                    #if best_value > alpha:
                    #    alpha = best_value
                    #    self.best_move = move
                    #    best_move = move

                    #    if alpha >= beta:
                    #        break

                # print(expanded, end=', ')
                #print("Best negamax value: ", best_value)
                return best_value, best_move


            self.elapsed = time.process_time()
            # state_copy = copy.deepcopy(self.env.current_state)

            # try:
            best_value, bm = negamax_alpha_beta(copy.deepcopy(self.env.current_state), 5, -100, 100, 1) # cp because used below
            #best_value, bm = minimax_ab(copy.deepcopy(self.env.current_state), 5, -100, 100, self.my_turn) # cp because used below
            time_in_sec = time.process_time() - self.elapsed
            print('\n ALPHABETA\n', '-'*26,
                '\n | BEST VALUE:', best_value,
                '\n | BEST MOVE:', [i + 1 for i in self.best_move], [i + 1 for i in bm], (bm == self.best_move),
                '\n | EXPANDED NODES:', round(self.expanded, 3),
                '\n | ELAPSED TIME:', round(time_in_sec, 3),
                '\n | NODES/SEC:', round((self.expanded / time_in_sec), 3),
                '\n', '-'*26, '\n'
            )
            # except TimeoutError:
            #     self.best_move = None


            self.best_move = bm # FIXME: This should be the same value but isnt


            if not self.best_move:
                legal_moves = self.env.get_legal_moves(copy.deepcopy(self.env.current_state))
                self.best_move = random.choice(legal_moves) if legal_moves else [9,8,7,6] # random at worst


            x1, y1, x2, y2 = [i + 1 for i in self.best_move] # TODO and check role to do "self.height - y2"

            # print('-'*52, x1, y1, x2, y2)

            # direction = 1
            # if self.role == 'black':
            #     direction = -1
            # y2 = y1 + direction * random.randint(1, 2)
            return "(move " + " ".join(map(str, [x1, y1, x2, y2])) + ")"
        else:
            return "noop"