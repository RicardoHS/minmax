"""
Rules:
- Must jump if you can
- Must multiple-jump if you can
- Kings can go backwards but move at the same pace as normal pieces
"""
from minmax_ai import AI

BLANK = " "
WALL = " "
PLAYER = "X"
OPP = "O"
PLAYER_KING = "K"
OPP_KING = "Q"

GHOST_PLAYER = "GX"
GHOST_OPP = "GO"
GHOST_C, GHOST_R = 7, 0

# colors
GREEN = '\033[92m'
RED = '\033[91m'
ENDC = '\033[0m'

def color_str(x):
    if x == PLAYER or x == PLAYER_KING:
        return GREEN + str(x) + ENDC + "   "
    if x == GHOST_PLAYER:
        return str(PLAYER) + "   "
    if x == GHOST_OPP:
        return str(OPP) + "   "
    return RED + str(x) + ENDC + "   "

# an implementation for tictactoe AI using minmax and alphabeta pruning
# board array access is board[col][row]

# boards are always squares
def make_board(width=8, black="X", white="O"):
    board = [[white, WALL] * (width / 2),
             [WALL, white] * (width / 2)]
    
    fst = [BLANK, WALL] * (width / 2)
    snd = [WALL, BLANK] * (width / 2)
    middle = [fst, snd] * ((width - 4) / 2)
    
    board.extend(middle)
    
    board.extend([[black, WALL] * (width / 2),
                  [WALL, black] * (width / 2)])
    
    # zip makes tuples so we re-list-ify the cols
    return map(list, zip(*board))

# TODO: draw a ghost where the piece moved from
def print_board(board):
    global GHOST_C, GHOST_R
    border = ["----"] * len(board)
    print
    for i in xrange(len(board[0])):
        print " | ".join(border)
        row = [board[j][i] for j in xrange(len(board))]
        row = map(lambda x: color_str(x), row)
        print " | ".join(row)
        n = [(j,i) for j in xrange(len(board))]
        n = map(lambda (y,x): " " + str(y) + " " + str(x) if y%2 == x%2 else "    ", n)
        print " | ".join(n)
    print " | ".join(border)
    board[GHOST_C][GHOST_R] = BLANK
    

# assumes that white pieces move forward from top to bottom (low to hi index)
# and black pieces move from bottom to top (high to low)
# returns a list of tuple (dc,dr) where dc dr are the deltas to get to the cell
# of the piece to be taken, NOT the cell after the jump
# i.e. (i + dc, j + dr) is the actual indices of the piece to take
# this is just the first piece to be taken, multiple jumps are not considered
def jump_moves(board, piece, i, j):
    num_cols, num_rows = len(board), len(board[0])
    white_forward = [(+1, +1), (-1, +1)]
    black_forward = [(+1, -1), (-1, -1)]
    
    neighbors = { PLAYER      : black_forward,
                  OPP         : white_forward,
                  PLAYER_KING : black_forward.extend(white_forward),
                  OPP_KING    : black_forward.extend(white_forward)
    }
    
    adj_deltas = neighbors[piece]
    
    # list of jumpable pieces
    jumpable = [OPP, OPP_KING] if piece == PLAYER else [PLAYER, PLAYER_KING]
    
    # to return
    moves = []
    for dc, dr in adj_deltas:
        jump_dc, jump_dr = dc * 2, dr * 2
        # don't consider jumps that jump off the board
        if not (0 <= i + jump_dc < num_cols and 0 <= j + jump_dr < num_rows):
            continue
        # check if adj space has opp then check if jump space is empty
        if board[i + dc][j + dr] in jumpable and board[i + jump_dc][j + jump_dr] == BLANK:
            moves.append((dc, dr))
            
    return moves

def move_moves(board, piece, i, j):
    num_cols, num_rows = len(board), len(board[0])
    white_forward = [(+1, +1), (-1, +1)]
    black_forward = [(+1, -1), (-1, -1)]
    
    neighbors = { PLAYER      : black_forward,
                  OPP         : white_forward,
                  PLAYER_KING : black_forward.extend(white_forward),
                  OPP_KING    : black_forward.extend(white_forward)
    }
    
    adj_deltas = neighbors[piece]

    # to return
    moves = []
    for dc, dr in adj_deltas:
        # bounds checking; don't move off board
        if not (0 <= i + dc < num_cols and 0 <= j + dr < num_rows):
            continue
        if board[i + dc][j + dr] == BLANK:
            moves.append((dc, dr))

    return moves

# a move is a 4-tuple (col, row, col_delta, row_delta)
def possible_moves(board, curr):  
    jumps = []
    moves = []

    # TODO cell == curr doesn't take into account kings
    make_move = lambda (dc, dr): (i, j, dc, dr)
    for i, col in enumerate(board):
        for j, cell in enumerate(col):
            if cell == curr:
                jump_deltas = jump_moves(board, cell, i, j)
                jumps.extend(map(make_move, jump_deltas))
                move_deltas = move_moves(board, cell, i, j)
                moves.extend(map(make_move, move_deltas))
                
    # if any piece can jump, a jump must be made
    if len(jumps) != 0:
        return jumps
    return moves
                
def is_valid_move(board, curr, f_c, f_r, t_c, t_r):
    pm = possible_moves(board, curr)
    pm = map(lambda (fc, fr, dc, dr): (fc, fr, fc + dc, fr + dr), pm)
    pm = filter(lambda move: move == (f_c, f_r, t_c, t_r), pm)
    return len(pm) != 0

# moves the piece at (f_c, f_r) to (t_c, t_r)
# does not check that move is valid so things will go horribly wrong
# if supplied with invalid moves
def next_state(old, curr, move):
    import copy
    new = copy.deepcopy(old)
    return next_state_helper(new, curr, move)

# created a seperate function to do the recursion so the board
# isn't copied multiple times
def next_state_helper(old, curr, (f_c, f_r, dc, dr)):
    t_c, t_r = f_c + dc, f_r + dr
    old[f_c][f_r] = BLANK
    
    # normal move
    if old[t_c][t_r] == BLANK:
        old[t_c][t_r] = curr
        
        # king me
        if t_r == 0 and curr == PLAYER:
            old[t_c][t_r] = PLAYER_KING
        if t_r == len(old[0]) and curr == OPP:
            old[t_c][t_r] = OPP_KING
        return old
    
    # jump
    old[t_c][t_r] = BLANK # "eat" the opponenets piece
    t_c, t_r = f_c + dc*2, f_r + dr*2
    old[t_c][t_r] = curr # move player to square after the jump
    
    # king me
    if t_r == 0 and curr == PLAYER:
        old[t_c][t_r] = PLAYER_KING
    if t_r == len(old[0]) and curr == OPP:
        old[t_c][t_r] = OPP_KING

    # check if another jump is possible from the new position (chained jumps)
    jump_deltas = jump_moves(old, curr, t_c, t_r)
    
    # TODO: what if there is more than one option to chain-jump?
    # ^ looks like chain jumping needs to be done in possible_moves :(
    if len(jump_deltas) != 0:
        # temp: just take the first chain-jump
        new_dc, new_dr = jump_deltas[0]
        return next_state_helper(old, curr, (t_c, t_r, new_dc, new_dr))
    return old

def get_winner(board):
    # at most there are three types of pieces, player1, player2, and the blank 
    all_cells = set([piece for col in board for piece in col])
    
    if len(all_cells) != 2:
        # no winner
        return None
        
    # the two elements are the blank and the winner
    all_cells.remove(BLANK)
    return all_cells.pop()

def game_over(board, player, opp):
    if get_winner(board) is not None:
        return True

    # can checkers ever draw?
    for col in board:
        for cell in col:
            if cell == BLANK:
                return False
    return True

# num of players pieces - num of opponents pieces
def evaluate(board, you, opp):
    all_cells = [piece for col in board for piece in col]
    return all_cells.count(you) - all_cells.count(opp)
                
# TODO
# doesn't do any error handling of bad input
def repl():
    global GHOST_C, GHOST_R
    board = make_board()

    from minmax_ai import AI
    ai = AI(ai_piece=OPP,
            opp=PLAYER,
            depth=3,
            game_over_fun=game_over,
            eval_fun=evaluate,
            moves_fun=possible_moves,
            next_state_fun=next_state)
    
    print "You are X"
    print "The numbers at the bottom-right corner of cells is the col-row number. Seperate the digits when entering you move"
    print "Enter your moves as: from_col from_row to_col to_row"
    print "NOTE: When jumping a piece, enter the from col-row and the col-row of the FIRST PIECE to jump, NOT the space after it. Chain jumps will automaticlaly be performed for you"
    print "Your pieces are in GREEN, your opponenets are RED, and the ghost of where you opponent was is in WHITE"

    while(True):
        print
        print "Your Turn: "
        print_board(board)
        input = raw_input()
        f_c, f_r, t_c, t_r = map(int, input.split())
      
        if not is_valid_move(board, PLAYER, f_c, f_r, t_c, t_r):
            print "Invalid move!"
            continue        
    
        board = next_state(board, PLAYER, (f_c, f_r, t_c- f_c, t_r - f_r))

        winner = get_winner(board)
        if game_over(board, PLAYER, OPP):
            if winner != None:
                if winner == PLAYER:
                    print "You win!"
                else:
                    print "You lose!"
            else:
                print "Draw!"
            break

        print 
        print "Their turn..."
    
        score, ai_move = ai.get_move(board)
        board = next_state(board, OPP, ai_move)
        ai_fc, ai_fr, ai_dc, ai_dr = ai_move
        GHOST_C, GHOST_R = ai_fc, ai_fr
        board[GHOST_C][GHOST_R] = GHOST_OPP
        print str((ai_fc, ai_fr)) + " -> " + str((ai_fc + ai_dc, ai_fr + ai_dr))

        winner = get_winner(board)    
        if game_over(board, PLAYER, OPP):
            if winner != None:
                if winner == PLAYER:
                    print "You win!"
                else:
                    print "You lose!"
            else:
                print "Draw!"
            break

if __name__ == "__main__":
    repl()

