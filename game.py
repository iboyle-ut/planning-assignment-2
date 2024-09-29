import numpy as np

class BoardState:
    """
    Represents a state in the game
    """

    def __init__(self):
        """
        Initializes a fresh game state
        """
        self.N_ROWS = 8
        self.N_COLS = 7

        self.state = np.array([1,2,3,4,5,3,50,51,52,53,54,52])
        self.decode_state = [self.decode_single_pos(d) for d in self.state]

        self.player0 = [0,1,2,3,4]
        self.player1 = [6,7,8,9,10]

    def update(self, idx, val):
        """
        Updates both the encoded and decoded states
        """
        self.state[idx] = val
        self.decode_state[idx] = self.decode_single_pos(self.state[idx])

    def make_state(self):
        """
        Creates a new decoded state list from the existing state array
        """
        return [self.decode_single_pos(d) for d in self.state]

    def encode_single_pos(self, cr: tuple):
        """
        Encodes a single coordinate (col, row) -> Z

        Input: a tuple (col, row)
        Output: an integer in the interval [0, 55] inclusive

        TODO: You need to implement this.
        """
        return int(cr[0] + (cr[1]*self.N_COLS))

    def decode_single_pos(self, n: int):
        """
        Decodes a single integer into a coordinate on the board: Z -> (col, row)

        Input: an integer in the interval [0, 55] inclusive
        Output: a tuple (col, row)

        TODO: You need to implement this.
        """
        return (int(n % self.N_COLS), int(n // self.N_COLS))

    def is_termination_state(self):
        """
        Checks if the current state is a termination state. Termination occurs when
        one of the player's move their ball to the opposite side of the board.

        You can assume that `self.state` contains the current state of the board, so
        check whether self.state represents a terminal board state, and return True or False.
        
        TODO: You need to implement this.
        """
        player1_wins = (self.decode_state[5][1] == (self.N_ROWS-1))
        player2_wins = (self.decode_state[11][1] == 0)
        return self.is_valid() & (player1_wins | player2_wins)

    def is_valid(self):
        """
        Checks if a board configuration is valid. This function checks whether the current
        value self.state represents a valid board configuration or not. This encodes and checks
        the various constrainsts that must always be satisfied in any valid board state during a game.

        If we give you a self.state array of 12 arbitrary integers, this function should indicate whether
        it represents a valid board configuration.

        Output: return True (if valid) or False (if not valid)
        
        TODO: You need to implement this.
        """
        #blocks must be on board
        valid_block_pos = [
            ((c >= 0) & (c < self.N_COLS)) & ((r >= 0) & (r < self.N_ROWS))
            for c, r in self.decode_state
        ]
        #blocks cannot overlap
        no_overlaps = len(np.unique(self.state[np.r_[0:5,6:11]])) == 10
        #ball must be on a block
        valid_ball_pos = (self.state[5] in self.state[0:5]) & (self.state[11] in self.state[6:11])
        return all(valid_block_pos) & no_overlaps & valid_ball_pos

class Rules:

    @staticmethod
    def single_piece_actions(board_state, piece_idx):
        """
        Returns the set of possible actions for the given piece, assumed to be a valid piece located
        at piece_idx in the board_state.state.

        Inputs:
            - board_state, assumed to be a BoardState
            - piece_idx, assumed to be an index into board_state, identfying which piece we wish to
              enumerate the actions for.

        Output: an iterable (set or list or tuple) of integers which indicate the encoded positions
            that piece_idx can move to during this turn.
        
        TODO: You need to implement this.
        """
        #store original loc
        orig_loc = board_state.state[piece_idx]
        #handle edge case where player has the ball
        if orig_loc in board_state.state[[5,11]]:
            return []
        #generate all 8 moves
        orig_loc_decoded = board_state.decode_state[piece_idx]
        moves = [
            (orig_loc_decoded[0]+x, orig_loc_decoded[1]+y)
            for (x, y) in [(2, 1), (1, 2), (-2, 1), (1, -2), (-1, 2), (2, -1), (-1, -2), (-2, -1)]
        ]
        #check valid before encoding
        moves = [
            board_state.encode_single_pos(m) for m in moves 
            if (m[0] >= 0) and (m[0] < board_state.N_COLS)
            and (m[1] >= 0) and (m[1] < board_state.N_ROWS)
        ]
        #keep if board would be valid with that move
        def check_valid(m):
            board_state.update(piece_idx, m)
            return board_state.is_valid()
        moves = [m for m in moves if check_valid(m)]
        #return the piece to its starting place
        board_state.update(piece_idx, orig_loc)
        return moves

    @staticmethod
    def single_ball_actions(board_state, player_idx):
        """
        Returns the set of possible actions for moving the specified ball, assumed to be the
        valid ball for plater_idx  in the board_state

        Inputs:
            - board_state, assumed to be a BoardState
            - player_idx, either 0 or 1, to indicate which player's ball we are enumerating over
        
        Output: an iterable (set or list or tuple) of integers which indicate the encoded positions
            that player_idx's ball can move to during this turn.
        
        TODO: You need to implement this.
        """
        #get each teams position
        teammates = board_state.player0 if player_idx == 0 else board_state.player1
        opponents = board_state.player1 if player_idx == 0 else board_state.player0
        #get ball 
        ball_pos = board_state.state[5] if player_idx == 0 else board_state.state[11]
        opp_pos = np.array(board_state.decode_state)[opponents] 

        def check_pass(pos1, pos2):
            pos1, pos2 = [board_state.decode_single_pos(p) for p in [pos1, pos2]]
            #pass along column if on same column
            if pos1[0] == pos2[0]:
                #and no opponents in rows between
                return not any(
                    ((opp[1] > pos1[1]) & (opp[1] < pos2[1])) | ((opp[1] > pos2[1]) & (opp[1] < pos1[1]))
                    for opp in opp_pos if opp[0] == pos1[0]
                )
            #pass along row if on same row
            elif pos1[1] == pos2[1]:
                #and no opponents in columns between
                return not any(
                    ((opp[0] > pos1[0]) & (opp[0] < pos2[0])) | ((opp[0] > pos2[0]) & (opp[0] < pos1[0]))
                    for opp in opp_pos if opp[1] == pos1[1]
                )
            #pass along diagonal if abs diff between rows and cols is the same
            elif abs(pos1[0]-pos2[0]) == abs(pos1[1]-pos2[1]):
                #and no opponents on diagonal between
                cols, rows = sorted([pos1[0], pos2[0]]), sorted([pos1[1], pos2[1]])
                return not any(
                    ((opp[0] > cols[0]) & (opp[0] < cols[1])) & ((opp[1] > rows[0]) & (opp[1] < rows[1]))
                    for opp in opp_pos if abs(opp[0]-pos1[0]) == abs(opp[1]-pos1[1])
                )
            else:
                return False

        #start from who has ball
        reachable = new_reachable = set([ball_pos])
        #record states that are so far unreachable
        unreachable = set(board_state.state[teammates]) - new_reachable
        #check whether unreachable states are reachable from new reachable states
        while len(new_reachable) > 0 and len(unreachable) > 0:
            new_reachable = set(u for u in unreachable for t in reachable if check_pass(t, u))
            reachable |= new_reachable
            unreachable -= new_reachable
        #remove balls current position
        return set(int(t) for t in reachable if t != ball_pos)

class GameSimulator:
    """
    Responsible for handling the game simulation
    """

    def __init__(self, players):
        self.game_state = BoardState()
        self.current_round = -1 ## The game starts on round 0; white's move on EVEN rounds; black's move on ODD rounds
        self.players = players

    def run(self):
        """
        Runs a game simulation
        """
        while not self.game_state.is_termination_state():
            ## Determine the round number, and the player who needs to move
            self.current_round += 1
            player_idx = self.current_round % 2
            ## For the player who needs to move, provide them with the current game state
            ## and then ask them to choose an action according to their policy
            action, value = self.players[player_idx].policy( self.game_state.make_state() )
            print(f"Round: {self.current_round} Player: {player_idx} State: {tuple(self.game_state.state)} Action: {action} Value: {value}")

            if not self.validate_action(action, player_idx):
                ## If an invalid action is provided, then the other player will be declared the winner
                if player_idx == 0:
                    return self.current_round, "BLACK", "White provided an invalid action"
                else:
                    return self.current_round, "WHITE", "Black probided an invalid action"

            ## Updates the game state
            self.update(action, player_idx)

        ## Player who moved last is the winner
        if player_idx == 0:
            return self.current_round, "WHITE", "No issues"
        else:
            return self.current_round, "BLACK", "No issues"

    def generate_valid_actions(self, player_idx: int):
        """
        Given a valid state, and a player's turn, generate the set of possible actions that player can take

        player_idx is either 0 or 1

        Input:
            - player_idx, which indicates the player that is moving this turn. This will help index into the
              current BoardState which is self.game_state
        Outputs:
            - a set of tuples (relative_idx, encoded position), each of which encodes an action. The set should include
              all possible actions that the player can take during this turn. relative_idx must be an
              integer on the interval [0, 5] inclusive. Given relative_idx and player_idx, the index for any
              piece in the boardstate can be obtained, so relative_idx is the index relative to current player's
              pieces. Pieces with relative index 0,1,2,3,4 are block pieces that like knights in chess, and
              relative index 5 is the player's ball piece.
            
        TODO: You need to implement this.
        """
        player_pieces = self.game_state.player0 if player_idx == 0 else self.game_state.player1
        piece_moves = {i:Rules.single_piece_actions(self.game_state, player_pieces[i]) for i in range(5)}
        ball_moves = [(5,m) for m in Rules.single_ball_actions(self.game_state, player_idx)]
        return [(i,m) for i in piece_moves for m in piece_moves[i]]+ball_moves

    def validate_action(self, action: tuple, player_idx: int):
        """
        Checks whether or not the specified action can be taken from this state by the specified player

        Inputs:
            - action is a tuple (relative_idx, encoded position)
            - player_idx is an integer 0 or 1 representing the player that is moving this turn
            - self.game_state represents the current BoardState

        Output:
            - if the action is valid, return True
            - if the action is not valid, raise ValueError
        
        TODO: You need to implement this.
        """
        team = self.game_state.player0 if player_idx == 0 else self.game_state.player1
        #validate ball
        if action[0] == 5:
            if action[1] not in self.game_state.state[team]:
                raise ValueError("ball not with player")
        else:

            c, r = self.game_state.decode_single_pos(action[1])
            if ((c < 0) & (c >= self.game_state.N_COLS)) | ((r < 0) & (r >= self.game_state.N_ROWS)):
                raise ValueError("invalid position")

            orig_pos = self.game_state.decode_state[action[0]+(player_idx*6)]
            if not (
                ((abs(orig_pos[0] - c) == 2) & (abs(orig_pos[1] - r) == 1)) |
                ((abs(orig_pos[0] - c) == 1) & (abs(orig_pos[1] - r) == 2))
            ):
                raise ValueError("invalid movement")

            if orig_pos == self.game_state.decode_state[team[-1]]:
                raise ValueError("can't move player with ball")

            if action[1] in self.game_state.state[np.r_[0:5,6:11]]:
                raise ValueError("overlapping with another player")
        return True
    
    def update(self, action: tuple, player_idx: int):
        """
        Uses a validated action and updates the game board state
        """
        offset_idx = player_idx * 6 ## Either 0 or 6
        idx, pos = action
        self.game_state.update(offset_idx + idx, pos)
