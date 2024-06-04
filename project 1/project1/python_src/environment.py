# import collections
import copy

########################

# State = collections.namedtuple('State', ['board', 'turn'])

########################

class State:
    def __init__(self, board, turn = True, moves = []):
        self.board = board
        self.turn = turn

    def __str__(self):
        ret = f"\n>> BOARD: {'W' if self.turn else 'B'} <<\n"
        for row in reversed(self.board):
            line = ""
            for col in row:
                line += str(col) + " "
            ret += line + "\n"
        return ret

    def __eq__(self, o):
        return self.board == o.board and self.turn == o.turn

    def __hash__(self):
        return hash(','.join(','.join([str(y) for y in self.board]))) + hash(str(self.turn))

########################

EMPTY_SQUARE = 0
P1 = 1
P2 = 2

def create_board(w, h):
    board = []
    board.append([P1] * w)
    board.append([P1] * w)
    for _ in range(h - 4):
        board.append([EMPTY_SQUARE] * w)
    board.append([P2] * w)
    board.append([P2] * w)

    return board

class Environment:

    def __init__(self, width, height, turn = True):
        self.width = width
        self.height = height
        self.current_state = State(create_board(width, height), turn)

    def get_legal_moves(self, state):
        moves = []
        board = state.board

        def onboard(x1, y1, x2, y2):
            return (x1 >= 0 and x1 < self.width
                and y1 >= 0 and y < self.height
                and x2 >= 0 and x2 < self.width
                and y2 >= 0 and y2 < self.height
            )

        def op(y, i):
            return (y + i) if state.turn else (y - i)

        def add_attack(x1, y1, x2, y2, piece):
            if onboard(x1, y1, x2, y2) and board[y2][x2] != piece and board[y2][x2] != EMPTY_SQUARE:
                moves.append([x1, y1, x2, y2])

        def add_move(x1, y1, x2, y2):
            if onboard(x1, y1, x2, y2) and board[y2][x2] == EMPTY_SQUARE:
                moves.append([x1, y1, x2, y2])

        def sqr():
            return P1 if state.turn else P2

        for y, row in enumerate(board):
            for x, square in enumerate(row):
                if  square == sqr():
                    add_move(x, y, x - 2, op(y, 1)) # move_left
                    add_move(x, y, x + 2, op(y, 1)) # move_right
                    add_move(x, y, x - 1, op(y, 2)) # move_up_left
                    add_move(x, y, x + 1, op(y, 2)) # move_up_right
                    add_attack(x, y, x - 1, op(y, 1), square) # attack_left
                    add_attack(x, y, x + 1, op(y, 1), square) # attack_right

        return moves

    def is_terminal(self, state):
        return (P1 in state.board[-1]) or (P2 in state.board[0]) or (not self.get_legal_moves(state))

    def do_move(self, state, move):
        x1, y1, x2, y2 = move

        piece = state.board[y1][x1]
        state.board[y1][x1] = EMPTY_SQUARE
        state.board[y2][x2] = piece

        state.turn = (not state.turn)

        return state

    def undo_move(self, state, move):
        x1, y1, x2, y2 = move

        piece = state.board[y2][x2]

        if y2 == y1 + 1 and (x2 == x1 + 1 or x2 == x1 - 1):
            state.board[y2][x2] = P2
        elif y2 == y1 - 1 and (x2 == x1 + 1 or x2 == x1 - 1):
            state.board[y2][x2] = P1
        else:
            state.board[y2][x2] = EMPTY_SQUARE

        state.board[y1][x1] = piece

        state.turn = (not state.turn)

        return state

    def evaluate_state(self, state):
        board = state.board
        white_pieces = 0
        # white_position = 0
        black_pieces = 0
        # black_position = 0

        most_advanced_white = 1 # 2 rows of whites, starts at 0
        most_advanced_black = 1 # 2 rows of blacks
        position = 0
        checkered = 0
        # plus for advancing, more minus for opponent advancing
        for y, row in enumerate(board):
            for x, piece in enumerate(row):
                if (board[self.height - 1][x] == P1):
                    return 100
                if board[0][x] == P2:
                    return -100



                if piece == P1:  # and y < black_advance:
                    # # more points for being on same colour squares
                    # checkered += 1 if (y % 2 == 0 and x % 2 == 0) or (y % 2 != 0 and x % 2 != 0) else 0
                    white_pieces += 1
                    # white_position += 1 + ((y + 1) * y)
                    position += (y)
                    most_advanced_white = max(most_advanced_white, y)
                if piece == P2:  # and y < black_advance:
                    # checkered -= 1 if (y % 2 == 0 and x % 2 == 0) or (y % 2 != 0 and x % 2 != 0) else 0
                    black_pieces += 1
                    # black_position += 1 + (((self.height - 1) - y) * y)
                    position -= ((self.height - 1) - y)
                    most_advanced_black = max(most_advanced_black, ((self.height - 1) - y))

        if not self.get_legal_moves(state) or white_pieces == 0 or black_pieces == 0: # draw
            return 0

        most_advanced = (-most_advanced_black) - (-most_advanced_white)
        pieces = white_pieces - black_pieces

        ret = ((most_advanced + pieces) / 2) + position + (0.05 * checkered)

        return ret


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
    assert len(legal_moves) == 22

    # check goal state
    assert env.is_terminal(env.current_state) == False

    # illegally move knight to end of board
    env.do_move(env.current_state, [0, 0, 4, 6])
    # print('11', env.current_state)
    assert env.is_terminal(env.current_state) == True

    # won game
    assert env.evaluate_state(env.current_state) == 100