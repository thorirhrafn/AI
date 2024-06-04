import collections

########################

class Knight:
    x_position
    y_position

def move_left(self):
    self.x_position += -2
    self.y_position += 1

def move_right(self):
    self.x_position += 2
    self.y_position += 1    

def move_up_left(self):
    self.x_position += -1
    self.y_position += 2

def move_up_right(self):
    self.x_position += 1
    self.y_position += 2

 def attack_left(self):
    self.x_position -= 1
    self.y_position += 1
       
 def attack_right(self):
    self.x_position -= 1
    self.y_position += 1

########################

State = collections.namedtuple('State',['white_knights','black_knights'])

########################

class Environment:
  width = 0
  height = 0
  white_knights = []
  black_knights = []
  current_state = None

  # initialize environment
    def __init__(self, board_width, board_height)
        self.width = board_width
        self.height = board_height
        #set up knights on the board
        for i in range(0:width-1):
            white_knight_1 = new Knight
            white_knight_1.y_position = 0
            white_knight_1.x_position = i
            self.white_knights.append(white_knight_1)
            white_knight_2 = new Knight
            white_knight_2.y_position = 1
            white_knight_2.x_position = i
            self.white_knights.append(white_knight_2)
            black_knight_1 = new Knight
            black_knight_1.y_position = height-2
            black_knight_1.x_position = i
            self.black_knights.append(black_knight_1)
            black_knight_2 = new Knight
            black_knight_2.y_position = height-1
            black_knight_2.x_position = i
            self.black_knights.append(black_knight_2)
            

        return self

    def get_current_state(self):
        return self.current_state

    def get_legal_actions(self, state, my_knight):
        actions = []
        can_move_left = True
        can_move_right = True
        can_move_up_left = True
        can_move_up_right = True

        for black_knight in self.black_knights
            #Check if a black knight can be attack
            if black_knight.x_position == my_knight.x_position + 1 and black_knight.y_position = my_knight.y_position+1:
                actions.append("ATTACK_RIGHT")
            if black_knight.x_position == my_knight.x_position - 1 and black_knight.y_position = my_knight.y_position+1:
                actions.append("ATTACK_LEFT")
            #check if a black knight blocks movement    
            if black_knight.x_position == my_knight.x_position - 2 and black_knight.y_position = my_knight.y_position+1:    
                can_move_left = False
            if black_knight.x_position == my_knight.x_position + 2 and black_knight.y_position = my_knight.y_position+1:    
                can_move_right = False
            if black_knight.x_position == my_knight.x_position - 1 and black_knight.y_position = my_knight.y_position+2:    
                can_move_up_left = False
            if black_knight.x_position == my_knight.x_position + 1 and black_knight.y_position = my_knight.y_position+2:    
                can_move_up_right = False
        #Check if friendly knighs block movement
        for friend in self.white_knights:        
            if friend.x_position == my_knight.x_position - 2 and friend.y_position = my_knight.y_position+1:    
                can_move_left = False
            if friend.x_position == my_knight.x_position + 2 and friend.y_position = my_knight.y_position+1:    
                can_move_right = False
            if friend.x_position == my_knight.x_position - 1 and friend.y_position = my_knight.y_position+2:    
                can_move_up_left = False
            if friend.x_position == my_knight.x_position + 1 and friend.y_position = my_knight.y_position+2:    
                can_move_up_right = False

        #Check if moves are within boundaries of the board        
        if my_knight.x_position - 2 < 0:
            can_move_left = False
        if my_knight.x_position + 2 >= width:
            can_move_right = False
        if my_knight.y_position + 2 >= height:
            can_move_up_left = False
            can_move_up_right = False            

        if can_move_left:
            actions.append("MOVE_LEFT")
        if can_move_right:
            actions.append("MOVE_RIGHT")
        if can_move_up_left:
            actions.append("MOVE_UP_LEFT")
        if can_move_up_right:
            actions.append("MOVE_UP_RIGHT")            

        return actions

    def get_next_state(self, state, action, knight):
        my_knight = knight in self.white_knights    

        if action == "ATTACK_LEFT":
            for black_knight in self.black_knights:
                if black_knight.x_position == my_knight.x_position - 1 and black_knight.y_position == my_knight.y_position + 1:
                    self.black_knights.remove(black_knight)
                    my_knight.attack_left

        elif action == "ATTACK_RIGHT":
            for black_knight in self.black_knights:
                if black_knight.x_position == my_knight.x_position - 1 and black_knight.y_position == my_knight.y_position + 1:
                    self.black_knights.remove(black_knight)
                    my_knight.attack_right
        
        elif action == "MOVE_LEFT":
            my_knight.move_left
        elif action == "MOVE_RIGHT":
            my_knight.move_right
        elif action == "MOVE_UP_LEFT":
            my_knight.move_up_left
        elif action == "MOVE_UP_RIGHT":
            my_knight.move_up_right

        return State(self.white_knights, self.black_knights)    
    

    def is_goal_state(self, state):
        for knight in state.white_knights:
            if knight.y_position == height-1
            return True
        return False      
  