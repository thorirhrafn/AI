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
    # override it to reset the agent
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

class TranspositionalTable():
    def __init__(self):
        self.table = dict()

    def get_key(self, state):
        return str(hash(state) % 512)

    def lookup(self, state):
        entry = self.table.get(self.get_key(state), None)
        if entry:
            return entry.get(hash(state), None)
        return None

    def store(self, **data):
        key = self.get_key(data['state'])
        if key not in self.table:
            self.table[key] = dict()
        self.table[key][hash(data['state'])] = data

    def __str__(self):
        ret = ""
        for key, val in self.table.items():
            ret += f"{key}, "
            for k in val:
                ret += f"({k}),"
        return ret


LOWERBOUND = -100
EXACT = 0
UPPERBOUND = 100

class Search():
    def __init__(self, env, tt = None, play_clock = 5):
        self.expanded = 0
        self.elapsed = 0
        self.best_move = []
        self.env = env
        self.play_clock = play_clock
        self.tt = tt

    def timeout(self):
        return (time.time() - self.elapsed + 0.1) >= self.play_clock

    ''' minimax with iterative depthening '''
    def minimax(self, state, depth, maximize = True):
        if self.timeout():
            raise TimeoutError

        if self.env.is_terminal(state) or (depth <= 0):
            return self.env.evaluate_state(state) * 0.999, None

        legal_moves = self.env.get_legal_moves(state)

        if maximize:
            max_val = -100
            for move in legal_moves:
                self.expanded += 1
                self.env.do_move(state, move)
                value, _ = self.minimax(state, depth - 1, False)
                self.env.undo_move(state, move)

                # max_val = max(max_val, value)
                if max_val <= value:
                    max_val = value
                    self.best_move = move

            return max_val, self.best_move
        else:
            min_val = 100
            for move in legal_moves:
                self.expanded += 1
                self.env.do_move(state, move)
                value, _ = self.minimax(state, depth - 1, True)
                self.env.undo_move(state, move)

                # min_val = min(min_val, value)
                if value <= min_val:
                    min_val = value
                    # self.best_move = move

            return min_val, self.best_move

    ''' minimax with alpha_beta pruning '''
    def minimax_ab(self, state, depth, alpha = -100, beta = 100, maximize = True):
        if self.timeout():
            raise TimeoutError

        if self.env.is_terminal(state) or (depth <= 0):
        # if self.env.is_terminal(state) or (depth <= 0) or (self.elapsed + 0.5 >= self.play_clock):
            return (self.env.evaluate_state(state) * 0.999), None

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
                self.env.do_move(state, move)
                value, _ = self.minimax_ab(state, depth - 1, beta, alpha, False)
                self.env.undo_move(state, move)

                # max_val = max(max_val, value)
                if max_val <= value:
                    max_val = value
                    self.best_move = move
                    best_move = move

                # alpha = max(alpha, value)
                # ab pruning
                if alpha <= value:
                    alpha = max_val
                    if beta <= alpha:
                        break

            # self.best_move = best_move
            return max_val, best_move

        else: # minimize
            min_val = 100
            best_move = []
            legal_moves.sort(key=move_order) # NO reverse
            for move in legal_moves:
                self.expanded += 1
                self.env.do_move(state, move)
                value, _ = self.minimax_ab(state, depth - 1, beta, alpha, True)
                self.env.undo_move(state, move)

                # min_val = min(min_val, value)
                if value <= min_val:
                    min_val = value
                    best_move = move
                    self.best_move = move

                # ab pruning
                if beta >= min_val:
                    beta = min_val
                    if beta <= alpha:
                        break

            return min_val, best_move

    # self.w_wins = 0
    # self.b_wins = 0

    def negamax(self, state, depth, alpha = -100, beta = 100, minmax = 1):
        if self.timeout():
            raise TimeoutError

        if self.env.is_terminal(state) or depth <= 0:
            return (minmax * (self.env.evaluate_state(state) * 0.999)), None

        # makeshift move order
        def move_order(move):
            _state = copy.deepcopy(state)
            return self.env.evaluate_state(self.env.do_move(_state, move))

        best_value = -100
        value = -100
        best_move = [4, 4, 4, 4]
        legal_moves = self.env.get_legal_moves(state)
        legal_moves.sort(key=move_order, reverse=(minmax == 1))
        for move in legal_moves:
            self.expanded += 1
            self.env.do_move(state, move)
            value = max(value, -self.negamax(state, depth - 1, -beta, -alpha, -minmax)[0])
            self.env.undo_move(state, move)

            # # b. wins vs. w. wins
            # if value == 100:
            #     self.w_wins += 1
            # if value == -100:
            #     self.b_wins += 1

            if best_value <= value: # if this value is higher then we should use this move
                best_value = value
                best_move = move
                self.best_move = move

            alpha = max(alpha, value)

            if alpha >= beta:
                break

        # self.best_move = best_move
        return value, best_move # TODO remove best_move


    def negamax_ab(self, state, depth, alpha = -100, beta = 100, minmax = 1):
        if self.timeout():
            raise TimeoutError

        if self.env.is_terminal(state) or depth <= 0:
            return (minmax * (self.env.evaluate_state(state) * 0.999)), None

        # makeshift move order
        def move_order(move):
            _state = copy.deepcopy(state)
            return self.env.evaluate_state(self.env.do_move(_state, move))

        best_value = -100
        value = -100
        best_move = [4, 4, 4, 4]
        legal_moves = self.env.get_legal_moves(state)
        legal_moves.sort(key=move_order, reverse=(minmax == 1))
        for move in legal_moves:
            self.expanded += 1
            child_state = self.env.do_move(state, move)
            value = max(value, -self.negamax_ab(child_state, depth - 1, -beta, -alpha, -minmax)[0])
            self.env.undo_move(state, move)

            if best_value <= value:
                best_value = value
                best_move = move
                self.best_move = move

            alpha = max(alpha, value)

            if alpha >= beta:
                break

        return value, best_move


    def negamax_ab_tt(self, state, depth, alpha = -100, beta = 100, minmax = 1):
        if self.timeout():
            raise TimeoutError

        alphaOrig = alpha

        lookup = None if (self.tt is None) else self.tt.lookup(state)
        if lookup is not None and lookup['depth'] >= depth:
            flag = lookup['flag']
            value = lookup['value']
            if flag == EXACT:
                return value, lookup['move']
            elif flag == LOWERBOUND:
                alpha = max(alpha, value)
            elif flag == UPPERBOUND:
                beta = min(beta, value)

            if alpha >= beta:
                return value, lookup['move']

        if self.env.is_terminal(state) or depth <= 0:
            return (minmax * (self.env.evaluate_state(state) * 0.999)), None

        # makeshift move order
        def move_order(move):
            _state = copy.deepcopy(state)
            return self.env.evaluate_state(self.env.do_move(_state, move))

        best_value = -100
        value = -100
        best_move = [4, 4, 4, 4]
        legal_moves = self.env.get_legal_moves(state)
        legal_moves.sort(key=move_order, reverse=(minmax == 1))
        for move in legal_moves:
            self.expanded += 1
            self.env.do_move(state, move)
            value = max(value, -self.negamax_ab_tt(state, depth - 1, -beta, -alpha, -minmax)[0])
            self.env.undo_move(state, move)

            if best_value <= value:
                best_value = value
                best_move = move
                self.best_move = move

            alpha = max(alpha, value)

            if alpha >= beta:
                break

        if self.tt is not None:
            if value <= alphaOrig:
                flag = UPPERBOUND
            elif value >= beta:
                flag = LOWERBOUND
            else:
                flag = EXACT

            self.tt.store(
                state = state,
                depth = depth,
                value = value,
                move = best_move,
                flag = flag,
            )

        return value, best_move


    def print_stats(self):
        '''
            Keep track of and output the number of state expansions (total and
            per second), current depth limit of your iterative deepening loop
            and run-time of the search for each iteration of iterative deepening
            and in total. These numbers are very useful to compare with others
            or between different version of your code to see whether your search
            is fast (many nodes per second) and the pruning works well (high
            depth, but fewer expanded nodes).
        '''
        time_in_sec = time.process_time() - self.elapsed
        print('\n ALPHABETA\n', '-'*26,
            '\n | BEST VALUE:', self.best_value,
            '\n | BEST MOVE:', [i + 1 for i in self.best_move],
            [i + 1 for i in self.search.best_move],
            # [i + 1 for i in bm], (bm == self.best_move),
            '\n | EXPANDED NODES:', round(self.search.expanded, 3),
            '\n | ELAPSED TIME:', round(time_in_sec, 3),
            '\n | NODES/SEC:', round((self.search.expanded / time_in_sec), 3),
            # '\n | bwins, wwins:', self.b_wins, self.w_wins,
            '\n', '-'*26, '\n'
        )

class MyAgent(Agent):
    role = None
    play_clock = None
    my_turn = False
    width = 0
    height = 0

    def get_depth(self):
        depth = 3
        if self.play_clock >= 5 and self.width == 3 and self.height == 5:
            depth = 8
        elif self.play_clock >= 5 and self.width == 5 and self.height == 5:
            depth = 6
        elif self.play_clock >= 10 and self.width == 6:
            depth = 4
        elif self.width == 7:
            if self.play_clock >= 10:
                depth = 4
            if self.play_clock >= 30:
                depth = 5
        elif self.width == 8:
            if self.play_clock >= 60:
                depth = 4
            if self.play_clock >= 90:
                depth = 5
        elif self.width == 9:
            if self.play_clock >= 90:
                depth = 4
            if self.play_clock >= 120:
                depth = 5

        print(f"-- Attempting depth {depth} --")
        return depth

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
        self.env = Environment(width, height) # "not" because we start with False
        print(f"\n\n--- PLAYING {role} ---")
        tt = TranspositionalTable()
        self.search = Search(self.env, tt, self.play_clock) # TODO Will this change between initializations?
        self.depth = self.get_depth()
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
            # print('Who\'s move was last?', 'WHITES' if not self.env.current_state.turn else 'BLACKS', self.env.current_state)
        else:
            print("first move!")

        # update turn (above that line it myTurn is still for the previous state)
        self.my_turn = not self.my_turn
        if self.my_turn:
            # TODO: 2. run alpha-beta search to determine the best move

            self.search.expanded = 0
            state_copy = copy.deepcopy(self.env.current_state)
            self.search.elapsed = time.time()
            starter = -1 if self.role == 'white' else 1

            try:
                # best_value, bm = self.search.negamax(state_copy, self.depth, -100, 100, starter)
                # best_value, bm = self.search.negamax_ab(state_copy, self.depth, -100, 100, starter)
                best_value, bm = self.search.negamax_ab_tt(state_copy, self.depth, -100, 100, starter)
                # best_value, bm = self.search.minimax(state_copy, self.depth - 1, -100, 100, starter)
                # best_value, bm = self.search.minimax_ab(state_copy, self.depth - 2, -100, 100, starter)
            except TimeoutError:
                print("--- TIMED OUT ---")
                best_value = -999
                bm = self.search.best_move

            self.best_move = self.search.best_move # FIXME: This should be the same value but isnt
            # self.best_move = bm # FIXME: This should be the same value but isnt

            # time_in_sec = time.process_time() - self.elapsed
            time_in_sec = time.time() - self.search.elapsed
            print('\n Search stats:\n', '-'*26,
                '\n | DEPTH:', self.depth,
                '\n | BEST VALUE:', best_value,
                '\n | BEST MOVE:', [i + 1 for i in self.search.best_move], [i + 1 for i in self.best_move], 
                (bm == self.search.best_move),
                '\n | EXPANDED NODES:', round(self.search.expanded, 3),
                '\n | ELAPSED TIME:', round(time_in_sec, 3),
                '\n | NODES/SEC:', round((self.search.expanded / time_in_sec), 3),
                # '\n | bwins, wwins:', self.b_wins, self.w_wins,
                # '\n | tt:', self.search.tt,
                '\n', '-'*26, '\n'
            )

            legal_moves = self.env.get_legal_moves(self.env.current_state)
            if not self.best_move or self.best_move not in legal_moves:
                if self.search.best_move and self.search.best_move in legal_moves:
                    self.best_move = self.search.best_move
                else:
                    self.best_move = random.choice(legal_moves) if legal_moves else [-2, -2, -2, -2] # random at worst, debug [-2]

            x1, y1, x2, y2 = [i + 1 for i in self.best_move]

            return "(move " + " ".join(map(str, [x1, y1, x2, y2])) + ")"
        else:
            return "noop"

    def cleanup(self, last_move):
        # add last move and reset the env
        move = [i - 1 for i in list(last_move)]
        self.env.do_move(self.env.current_state, move)
        print('--- DONE ---')
        print(self.env.current_state)


if '__main__' == __name__:
    agent = MyAgent()
    agent.start(role = 'white', width = 5, height = 5, play_clock = 10)
    print(agent.depth)
    assert agent.depth == 6

    agent.next_action(False)
    agent.next_action([i + 1 for i in agent.best_move])
    print(agent.env.current_state)

    assert not agent.env.is_terminal(agent.env.current_state)

    def do_moves():
        if (agent.env.is_terminal(agent.env.current_state)):
            print('--- FIN ---')
            return False

        legal_moves = agent.env.get_legal_moves(agent.env.current_state)
        agent.next_action([i + 1 for i in random.choice(legal_moves)])
        print(agent.env.current_state)
        agent.next_action([i + 1 for i in agent.best_move]) # adds last white move to current_state
        print(agent.env.current_state)
        return True


    for _ in range(0,10):
        if not do_moves():
            assert agent.env.is_terminal(agent.env.current_state)
            break


    # legal_moves = agent.env.get_legal_moves(agent.env.current_state)
    # agent.next_action([i + 1 for i in random.choice(legal_moves)])
    # # agent.next_action((4, 3, 5, 1))
    # # agent.next_action([i + 1 for i in agent.best_move])
    # agent.next_action([i + 1 for i in agent.best_move])
    # print(agent.env.current_state)