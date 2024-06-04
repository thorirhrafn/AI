# import collections
import copy


########################

# State = collections.namedtuple('State', ['board', 'turn'])

########################

class State:
    def __init__(self, board, turn=True):
        self.turn = turn
        self.board = board

    def __str__(self):
        ret = "\n>> BOARD <<\n"
        for row in reversed(self.board):
            line = ""
            for col in row:
                line += str(col) + " "
            ret += line + "\n"
        return ret

    def __eq__(self, o):
        return self.board == o.board and self.turn == o.turn


########################

EMPTY_SQUARE = 0
P1 = 1
P2 = -1


class Environment:

    def __init__(self, width, height, turn=True):
        self.width = width
        self.height = height
        self.board = self.create_board()
        self.current_state = State(self.board, turn)  # TODO Perhaps add legal_states??? Or leave for TT

    def create_board(self):
        board = []
        board.append([P1] * self.width)
        board.append([P1] * self.width)
        for _ in range(self.height - 4):
            board.append([EMPTY_SQUARE] * self.width)
        board.append([P2] * self.width)
        board.append([P2] * self.width)

        return board

    '''
        The whole point of get_legal_moves is to be used in the search when you
        generate successor nodes. The search does not even care what a move
        looks like. All it cares about is getting a list of moves to iterate
        over and put into get_next_state one by one so it can create the
        successor states.
    '''

    def get_legal_moves(self, state):
        moves = []
        board = state.board

        def onboard(x, y):
            try:
                return (board[y][x] != None and x >= 0 and y >= 0)
            except IndexError:
                return False

        def add_move(x1, y1, x2, y2, sqr=EMPTY_SQUARE):
            if onboard(x2, y2) and board[y2][x2] == sqr:  # on the board and empty or opposition
                moves.append([x1, y1, x2, y2])

        def op(y, i):
            return (y + i) if state.turn else (y - i)

        for y, row in enumerate(board):
            for x, _ in enumerate(row):
                if onboard(x, y) and board[y][x] == P1:
                    add_move(x, y, x - 2, op(y, 1))  # move_left
                    add_move(x, y, x + 2, op(y, 1))  # move_right
                    add_move(x, y, x - 1, op(y, 2))  # move_up_left
                    add_move(x, y, x + 1, op(y, 2))  # move_up_right
                    add_move(x, y, x - 1, op(y, 1), P2)  # attack_left
                    add_move(x, y, x + 1, op(y, 1), P2)  # attack_right

        return moves

    def is_terminal(self, state):
        return (state.turn and P1 in state.board[-1]) or (not state.turn and P2 in state.board[0]) or (
            not self.get_legal_moves(state))
        # FIXME: Check if legal_moves is enough

        # check if there is a {role}-knight in top row
        goal_row = self.height - 1 if self.r == P1 else 0
        return self.r in state.board[goal_row] or (not self.get_legal_moves(state))

    '''
        [...] you have a class Environment with a current_state and some methods like
        legal_actions(state), get_next_state(state, action), is_terminal(state),
        evaluate(state) that you need to search through the state space. Instead of
        get_next_state, you could also have do_move(state, action) and
        undo_move(state, action), they serve essentially the same purpose, but
        modify the given state instead of creating a new one, which is more
        efficient in the search. The State class is really just a container to keep
        the information about a state that you need (such as the board and whose
        turn it is). In simple environments, you may not even need a special class
        for this. A built-in type might suffice.
    '''

    def do_move(self, state, move):
        ''' move = [x1, y1, x2, y2] '''
        x1, y1, x2, y2 = [i - 1 for i in move]

        piece = state.board[y1][x1]
        state.board[y1][x1] = EMPTY_SQUARE
        state.board[y2][x2] = piece

        state.turn = (not state.turn)

        return state

    def undo_move(self, state, move):
        x1, y1, x2, y2 = [i - 1 for i in move]

        piece = state.board[y2][x2]

        # replace capture
        if y2 == y1 + 1 and (x2 == x1 + 1 or (x2 == x1 - 1)):
            state.board[y2][x2] = P2 if state.turn else P1
        else:
            state.board[y2][x2] = EMPTY_SQUARE

        state.board[y1][x1] = piece
        # for row in state.board:
        #     row.reverse()
        # state.board.reverse()
        # state.board = state.board[::-1]
        state.turn = (not state.turn)

        return state

    def evaluate_state(self, state):
        # value = 0
        board = state.board
        legal_moves = self.get_legal_moves(state)

        # if there is a white piece in blacks end row then white has won
        if (P1 in board[-1]):
            return 100  # always maximising for some reason

        # if there are no legal moves available the game is a draw, return 0
        if not legal_moves:
            # print('*'*44, 'IS DRAW')
            return 0

        # # check if kill is possible
        #for move in legal_moves:
        #    x1, y1, x2, y2 = [i - 1 for i in move]
        #    if P1:
        #         if board[y1+1][x1+1] == board[y2][x2] or board[y1+1][x1-1] == board[y2][x2]:
        #                     #(y1+1 == y2 and x1+1 == x2) or (y1+1 == y2 and x1-1 == x2):
        #            return 66
        #    elif P2:
        #         if board[y1 - 1][x1 + 1] == board[y2][x2] or board[y1 - 1][x1 - 1] == board[y2][x2]:
        #                    #if (y1-1 == y2 and x1+1 == x2) or (y1-1 == y2 and x1-1 == x2):
        #            return -66

        # if there is a black piece in whites end row then black has won
        if P2 in board[0]:
            # print('*'*44, 'IS P1', 'NO' if self.r == P2 else 'YES')
            return -100

        # find the white and black pieces that have advanced the most and compare them
        white_material = 0
        white_position = 0
        black_material = 0
        black_position = 0
        for x in range(0, self.width):
            for y in range(0, self.height):
                if board[y][x] == P1:  # and y > white_advance:
                    white_material += 1
                    white_position += y + 1
                    # if piece is being protected add to value for white
                    if (y - 1) > 0 and (x - 1) > 0:
                        if board[y - 1][x - 1] == P1:
                            white_position += 0.5
                    if (y - 1) > 0 and (x + 1) < self.width:
                        if board[y - 1][x + 1] == P1:
                            white_position += 0.5
                if board[y][x] == P2:  # and y < black_advance:
                    black_material += 1
                    black_position += (self.height - y) + 1
                    # if piece is being protected add to value for black
                    if (y + 1) < self.height and (x - 1) > 0:
                        if board[y + 1][x - 1] == P2:
                            black_position += 0.5
                    if (y + 1) < self.height and (x + 1) < self.width:
                        if board[y + 1][x + 1] == P1:
                            black_position += 0.5
        # return the comparison value of whites and blacks advances
        white_score = white_material + white_position
        black_score = black_material + black_position
        return white_score - black_score  # - white_advance
        # return black_advance - ((self.height-1)-white_advance)


if '__main__' == __name__:
    env = Environment(5, 7, 'white')
    env.do_move(env.current_state, [2, 2, 3, 4])
    print('1', env.current_state)
    state1 = copy.deepcopy(env.current_state)
    env.do_move(env.current_state, [2, 1, 1, 3])
    # print('2', env.current_state)
    state2 = copy.deepcopy(env.current_state)
    env.undo_move(env.current_state, [2, 1, 1, 3])

    # print('3', env.current_state, '\n4', state1)
    # state after undo of 2nd move should be same as after first move
    assert state1.board == env.current_state.board
    # state after 2nd move should not be same as after undo
    assert state2.board != env.current_state.board

    # legal moves should be 16
    legal_moves = env.get_legal_moves(env.current_state)
    assert len(legal_moves) == 21

    # check goal state
    assert env.is_terminal(env.current_state) == False

    # illegally move knight to end of board
    env.do_move(env.current_state, [1, 1, 5, 7])
    # print('11', env.current_state)
    assert env.is_terminal(env.current_state) == True

    # won game
    assert env.evaluate_state(env.current_state) == 100
