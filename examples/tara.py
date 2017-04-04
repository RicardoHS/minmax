from minmax_ai import AI, print_board

blank = "-"
PAWN_PLAYER = "X"
PAWN_IA = "O"

# boards are always squares
def make_board(width):
    return [[blank] * width for _ in xrange(width)]
              
def possible_moves(board, curr):  
    print [(0,y) for y in xrange(len(board))]
    return [(0,y) for y in xrange(len(board))]

def moveXr(board, col, current,old_piece):
    if len(board) != (current+1) :
        if board[col][current] != blank :
            moveXr(board,col,current+1,board[col][current])
            board[col][current] = old_piece
        else :
            board[col][current] = old_piece
    else :
        board[col][current] = old_piece

def moveYr(board, row, current,old_piece):
    if len(board) != (current+1) :
        if board[current][row] != blank :
            moveYr(board,row,current+1,board[current][row])
            board[current][row] = old_piece
        else :
            board[current][row] = old_piece
    else :
        board[current][row] = old_piece

def moveX(board, col):
    import copy
    new = copy.deepcopy(board)
    moveXr(new,col,0,PAWN_PLAYER)
    return new

def moveY(board, row):
    import copy
    new = copy.deepcopy(board)
    moveYr(new,row,0,PAWN_IA)
    return new

# create a new board but with position @(col, row) changed to @player
def next_state(old, player, (col,row)):
    if player == PAWN_PLAYER:
        new = moveX(old, col)
        new[col][0] = player
    else :
        new = moveY(old,row)
        new[0][row] = player

    return new

def checkNeighborXnodes(board, x, y):
    if x > 0 and x < (len(board)-1):
        if board[x-1][y]  == PAWN_PLAYER or board[x][y] == PAWN_PLAYER or board[x+1][y] == PAWN_PLAYER  :
            return True
    elif x == 0:
        if board[x][y] == PAWN_PLAYER  or board[x+1][y] == PAWN_PLAYER :
            return True
    else : #x == len(board)-1
        if board[x-1][y] == PAWN_PLAYER  or board[x][y] == PAWN_PLAYER :
            return True
    return False

def checkPathXr(board, x, y):
    if y == (len(board)-1):
        return checkNeighborXnodes(board, x, y)
    else:
        temp = False
        if x > 0 and x < (len(board)-1):
            if board[x-1][y] == PAWN_PLAYER :
                temp = checkPathXr(board,x-1,y+1)
            if temp == False and board[x][y] == PAWN_PLAYER:
                temp = checkPathXr(board,x,y+1)
            if temp == False and board[x+1][y] == PAWN_PLAYER:
                temp = checkPathXr(board,x+1,y+1)
            return temp
        elif x == 0:
            if board[x][y] == PAWN_PLAYER:
                temp = checkPathXr(board,x,y+1)
            if temp == False and board[x+1][y] == PAWN_PLAYER:
                temp = checkPathXr(board,x+1,y+1)
            return temp
        else : #x == len(board)-1
            if board[x-1][y] == PAWN_PLAYER:
                temp = checkPathXr(board,x-1,y+1)
            if temp == False and board[x][y] == PAWN_PLAYER:
                temp = checkPathXr(board,x,y+1)
            return temp

def checkNeighborYnodes(board, x, y):
    if y > 0 and y < (len(board)-1):
        if board[x][y-1]== PAWN_IA or board[x][y]== PAWN_IA or board[x][y+1] == PAWN_IA :
            return True
    elif y == 0:
        if board[x][y]== PAWN_IA or board[x][y+1] == PAWN_IA :
            return True
    else : #y == len(board)-1
        if board[x][y-1]== PAWN_IA or board[x][y] == PAWN_IA :
            return True
    return False

def checkPathYr(board, x, y):
    if x == (len(board)-1):
        return checkNeighborYnodes(board, x, y)
    else:
        temp = False
        if y > 0 and y < (len(board)-1):
            if board[x][y-1] == PAWN_IA :
                temp = checkPathYr(board,x+1,y-1)
            if temp == False and board[x][y] == PAWN_IA:
                temp = checkPathYr(board,x+1,y)
            if temp == False and board[x][y+1] == PAWN_IA:
                temp = checkPathYr(board,x+1,y+1)
            return temp
        elif y == 0:
            if board[x][y] == PAWN_IA:
                temp = checkPathYr(board,x+1,y)
            if temp == False and board[x][y+1] == PAWN_IA:
                temp = checkPathYr(board,x+1,y+1)
            return temp
        else : #y == len(board)-1
            if board[x][y-1] == PAWN_IA:
                temp = checkPathYr(board,x+1,y-1)
            if temp == False and board[x][y] == PAWN_IA:
                temp = checkPathYr(board,x+1,y)
            return temp

def get_winner(board):
    verticalWinner, horizontalWinner, draw = False, False, False
    
    #check vertical path
    for i in range(len(board)):
        if checkPathXr(board, i, 0) :
            verticalWinner = True
            break
    
    #check orizontal path
    for i in range(len(board)):
        if checkPathYr(board, 0, i) :
            horizontalWinner = True
            break

    if verticalWinner and horizontalWinner :
        draw = True

    return verticalWinner, horizontalWinner, draw
    

def game_over(board, player, opp):
    vW, hW, draw = get_winner(board)

    if vW or hW :
        return True
    else:
        return False

# returns 10 if @you is the winner, -10 if @you is the loser
# and 0 otherwise (tie, or game not over)
def evaluate(board, you, _):
    vW, hW, draw = get_winner(board)
    
    if you == PAWN_PLAYER:
        return 10 if vW else -10
    else:
        return 10 if hW else -10
                

# doesn't do any error handling of bad input
def repl():
    board = make_board(5)
    player = PAWN_PLAYER
    opp = PAWN_IA

    ai = AI(ai_piece=opp,
            opp=player,
            depth=9,
            game_over_fun=game_over,
            eval_fun=evaluate,
            moves_fun=possible_moves,
            next_state_fun=next_state)
    
    print "You are X"
    print "Enter your move"

    while(True):
        print
        print "Your Turn: "
        print_board(board)
        #input = raw_input()
        try:
            y = 0
            x = int(raw_input()) 
            if x > 4 or x < 0:
                print "Invalid move! Must be a number between 0-4." 
                continue
        except IndexError:
            print "Invalid move! Out of board cordinates."
            continue
        except ValueError:
            print "Invalid move!"
            continue
    
        board = next_state(board, player, (x,y))
        print_board(board)
        vW,hW,draw = get_winner(board)    
        print vW, hW, draw
        if game_over(board, player, opp):
            if vW :
                print "The real player win!"
            elif hW:
                print "The IA win!"
            else:
                print "Draw!"
            break
        print 
        print "Their turn..."
        
        #IA controls
        #score, ai_move = ai.get_move(board)
        #print ai_move
        #board = next_state(board, opp, ai_move)
        #End IA controls

        #Player2 controls
        '''
        while True:
            try:
                y = int(raw_input())
                x = 0 
                if y > 4 or y < 0:
                    print "Invalid move! Must be a number between 0-4." 
                    continue
                break
            except IndexError:
                print "Invalid move! Out of board cordinates."
                continue
            except ValueError:
                print "Invalid move!"
                continue
        board = next_state(board, opp, (x,y))
        #'''
        #End player2 controls

        print_board(board)
        vW,hW,draw = get_winner(board)    
        print vW, hW, draw
        if game_over(board, player, opp):
            if hW :
                print "The IA win!"
            elif vW:
                print "The real player win!"
            else:
                print "Draw!"
            break


if __name__ == "__main__":
    repl()
