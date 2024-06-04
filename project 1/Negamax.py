def negamax(state, depth, minmax)
                if self.env.is_terminal(state) or depth <= 0:
                    return minmax * self.env.evaluate_state(state)
                
                max_value = -100
                best_move = []
                legal_moves = self.env.get_legal_moves(state)
                for move in legal_moves:
                    self.env.do_move(state, move)
                    next_state = self.env.get_legal_moves(state)
                    value = -negamax(next_state, depth-1, -minmax)
                    if value > max_value:
                        max_value = value
                        if depth == max_depth:
                            best_move = move
                    self.env.undo_move(state, move)
                
                return max_value   