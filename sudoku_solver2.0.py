##############################################
# Generic backtracking-based puzzle solver from https://www.kosbie.net/cmu/fall-19/15-112/notes/notes-recursion-part2.html
#
# Subclass this class to solve your puzzle
# using backtracking.
#
# To see how useful backtracking is, run with checkConstraints=True
# and again with checkConstraints=False
# You will see the number of total states go up (probably by a lot).
##############################################

import copy, time

class BacktrackingPuzzleSolver(object):
    def solve(self, checkConstraints=True, printReport=False):
        self.moves = [ ]
        self.states = set()
        # If checkConstraints is False, then do not check the backtracking
        # constraints as we go (so instead do an exhaustive search)
        self.checkConstraints = checkConstraints
        # Be sure to set self.startArgs and self.startState in __init__
        self.startTime = time.time()
        self.solutionState = self.solveFromState(self.startState)
        self.endTime = time.time()
        if (printReport): self.printReport()
        return (self.moves, self.solutionState)

    def printReport(self):
        print()
        print('***********************************')
        argsStr = str(self.startArgs).replace(',)',')') # remove singleton comma
        print(f'Report for {self.__class__.__name__}{argsStr}')
        print('checkConstraints:', self.checkConstraints)
        print('Moves:', self.moves)
        print('Solution state: ', end='')
        if ('\n' in str(self.solutionState)): print()
        print(self.solutionState)
        print('------------')
        print('Total states:', len(self.states))
        print('Total moves: ', len(self.moves))
        millis = int((self.endTime - self.startTime)*1000)
        print('Total time:  ', millis, 'ms')
        print('***********************************')

    def solveFromState(self, state):
        if state in self.states:
            # we have already seen this state, so skip it
            return None
        self.states.add(state)
        if self.isSolutionState(state):
            # we found a solution, so return it!
            return state
        else:
            legalMoves = self.getLegalMoves(state)
            for i in range(len(legalMoves)): # the loop is modified based on the original backtracking solver
                for k in range(2, len(legalMoves[i])): # [x, y,nums]
                    move = legalMoves[i][0:2]
                    move.append(legalMoves[i][k]) #[x, y, num]
                    # 1. Apply the move
                    childState = self.doMove(state, move)
                    # 2. Verify the move satisfies the backtracking constraints
                    #    (only proceed if so)
                    if ((self.stateSatisfiesConstraints(childState)) or
                        (not self.checkConstraints)):
                        # 3. Add the move to our solution path (self.moves)
                        self.moves.append(move)
                        # 4. Try to recursively solve from this new state
                        result = self.solveFromState(childState)
                        # 5. If we solved it, then return the solution!
                        if result != None:
                            return result
                        # 6. Else we did not solve it, so backtrack and
                        #    remove the move from the solution path (self.moves)
                        self.moves.pop()
            return None

    # You have to implement these:

    def __init__(self):
        # Be sure to set self.startArgs and self.startState here
        pass

    def stateSatisfiesConstraints(self, state):
        # return True if the state satisfies the solution constraints so far
        raise NotImplementedError

    def isSolutionState(self, state):
        # return True if the state is a solution
        raise NotImplementedError

    def getLegalMoves(self, state):
        # return a list of the legal moves from this state (but not
        # taking the solution constraints into account)
        raise NotImplementedError

    def doMove(self, state, move):
        # return a new state that results from applying the given
        # move to the given state
        raise NotImplementedError

# sudoku solver

class State(object):
    def __eq__(self, other): return (other != None) and self.__dict__ == other.__dict__
    def __hash__(self): return hash(str(self.__dict__)) 
    def __repr__(self): return str(self.__dict__)

class SudokuState(State):
    def __init__(self, board, numberPositions):
       self.board = board
       self.numberPositions = numberPositions
       # numerPositions: array with [x, y, num] position and number placed
    def __repr__(self):
        return str(self.board)

class SudokuSolver (BacktrackingPuzzleSolver):
    def __init__(self, board):
        self.board = board
        self.startArgs = (board, )
        self.startState = SudokuState(board, [[]])
       
    @staticmethod
    def areLegalValues(values):  
        for i in range (1,10):
            if (values.count(i)>1):
                return False
        return True

    def isLegalRow(self, board, row):
        return self.areLegalValues(board[row])

    def isLegalCol(self, board, col):
        a = []
        for index in range (len(board)):
            a.append(board[index][col])
        return self.areLegalValues(a)

    def isLegalBlock(self, board, block):
        row = block//3*3
        col = (block-row)*3
        a = []
        for r in range (3):
            for c in range (3):
                a.append(board[row+r][col+c])
        return self.areLegalValues(a)
        
    def stateSatisfiesConstraints(self, state):
        for r in range (len(self.board)):
            if (self.isLegalRow(state.board, r)==False or
            self.isLegalCol(state.board, r)==False or
            self.isLegalBlock(state.board, r)==False):
                return False
        return True

    def isSolutionState(self, state):
        # sum of all numbers should be (1+2..+9)*9 = 405 
        # repeating numbers already checked
        if (sum(sum(state.board,[]))==405 and self.stateSatisfiesConstraints(state)==True):
            return True
        return False

    def getLegalMoves(self, state):
        # the leftover 0s on the board with choices of 1-9
        # location of the last move with the choices of n+1 - 9
        if (state.numberPositions != [[]]):
            [x, y, num] = state.numberPositions
            if (num != 9):
                spaceLeft = [[x, y]+list(range(num+1, 10))]
            else:
                spaceLeft = []
        else:
            spaceLeft = []
        # spaceLeft = [state.numberpositions[x, y, (the rest of the numbers)] 
        for i in (range(len(state.board))):
            for j in (range(len(state.board))):
                if (state.board[i][j]==0):
                    spaceLeft.append([i,j]+list(range(1, 10))) #row,col, available nums
                    #[x, y, nums]
        return spaceLeft 

    def doMove(self, state, move):
        # update tate.board here 
        # move: [x, y, num]
        [x, y, num] = move
        updatedBoard = copy.deepcopy(state.board)
        updatedBoard[x][y] = num
        return SudokuState(updatedBoard, move)
        
# board=[
#     [ 1, 4, 0, 0, 2, 5, 0, 0, 0],
#     [ 0, 0, 0, 0, 4, 0, 0, 7, 3],
#     [ 7, 8, 0, 9, 0, 0, 0, 4, 5],
#     [ 0, 0, 7, 5, 0, 9, 0, 3, 2],
#     [ 0, 3, 9, 0, 0, 2, 0, 8, 0],
#     [ 8, 0, 2, 3, 0, 4, 7, 0, 0],
#     [ 0, 0, 1, 0, 5, 0, 6, 0, 0],
#     [ 0, 2, 0, 6, 0, 3, 8, 5, 7],
#     [ 5, 0, 0, 2, 9, 0, 0, 0, 0]
#     ]
board=[
    [ 0, 8, 0, 6, 7, 2, 5, 0, 1],
    [ 7, 5, 2, 8, 3, 1, 6, 4, 9],
    [ 0, 1, 0, 5, 4, 0, 8, 2, 7],
    [ 2, 0, 8, 0, 5, 7, 4, 9, 6],
    [ 5, 4, 7, 0, 0, 6, 2, 1, 8],
    [ 6, 0, 1, 2, 8, 4, 0, 5, 0],
    [ 9, 2, 4, 7, 6, 3, 0, 8, 5],
    [ 0, 7, 3, 4, 1, 5, 0, 6, 2],
    [ 1, 6, 5, 0, 2, 0, 3, 7, 4]
        ]


SudokuSolver(board).solve(printReport=True)
