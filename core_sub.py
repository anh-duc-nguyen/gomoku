from enum import Enum
from random import randint
from time import sleep

SIZE = 5 
class Piece(Enum):
    """A piece on the board can be either empty, black, or white."""
    BLACK = 0
    WHITE = 1
    EMPTY = 2


class Player:
    def alphabeta_search(self, game):
        moves = game.legal_moves()
        return moves[randint(0, len(moves) - 1)]


def play_gomoku(player0, player1):
    # Set-up logic
    players = (player0, player1)
    game = Game(SIZE, SIZE)

    while True:
        for player in players:
            move = player.alphabeta_search(game)
            game.make_move(move)
            game.display()

            if game.terminal_test():
                print("Game over")
                return

            sleep(3)


class Game:
    """A game is similar to a problem, but it has a utility for each
    state and a terminal test instead of a path cost and a goal
    test. To create a game, subclass this class and implement
    legal_moves, make_move, utility, and terminal_test. You may
    override display and successors or you can inherit their default
    methods. You will also need to set the .initial attribute to the
    initial state; this can be done in the constructor."""

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.cells = [[Piece.EMPTY for column in range(width)]
                      for row in range(height)]
        self.num_moves = 0

    def legal_moves(self):
        """Return a list of the allowable moves at this point."""
        moves = []
        for row in range(self.height):
            for col in range(self.width):
                if self.cells[row][col] == Piece.EMPTY:
                    moves.append((row, col))
        return moves

    def make_move(self, move):
        """Return the state that results from making a move from a state."""
        (row, col) = move
        self.cells[row][col] = self.to_move()
        self.num_moves += 1

    # def utility(self, state, player):
    #     "Return the value of this final state to player."
    #     abstract()

    def terminal_test(self):
        directions = [[1, 0], [0, 1], [1, 1], [1, -1]]
        for row in range(self.height):
            for col in range(self.width):
                if self.cells[row][col] != Piece.EMPTY:
                    for direction in directions:
                        if self._check_direction(row, col, direction):
                            return True
        return False

    def _check_direction(self, row, column, direction):
        [dr, dc] = direction
        piece = self.cells[row][column]

        # Obtain the maximum chain containing this piece by searching for the
        # position with the maximum/minimum row and column values that has
        # a different piece type than the one being assigned
        min_row, min_column = row - dr, column - dc
        while (self.is_legal_position(min_row, min_column) and
               self.cells[min_row][min_column] == piece):
            min_row -= dr
            min_column -= dc
        max_row, max_column = row + dr, column + dc
        while (self.is_legal_position(max_row, max_column) and
               self.cells[max_row][max_column] == piece):
            max_row += dr
            max_column += dc

        # Get the length of the resulting streak. The chain length is equal to
        # the difference in row values or in column values.
        length = (abs(max_row - min_row) - 1 if dr != 0
                  else abs(max_column - min_column) - 1)

        if length != SIZE:
            return False

        # Winning chain can border the board boundary
        if (not self.is_legal_position(min_row, min_column) or
                not self.is_legal_position(max_row, max_column)):
            return True

        # Winning chain must not be surrounded by two pieces of opposite type
        return (self.cells[min_row][min_column] == Piece.EMPTY or
                self.cells[max_row][max_column] == Piece.EMPTY)

    def to_move(self):
        """Return the player whose move it is in this state."""
        return Piece.BLACK if self.num_moves % 2 == 0 else Piece.WHITE

    def display(self):
        """Print or otherwise display the state."""
        symbols = ['x', 'o', '-']
        for row in range(self.height):
            for col in range(self.width):
                print(symbols[self.cells[row][col].value], end = ' ')
            print('\n')
        print('\n')

    def successors(self, state):
        """Return a list of legal (move, state) pairs."""
        m = [(move, self.make_move(move, state))
             for move in self.legal_moves(state)]
        # print "succ len: ", len(m)
        return m

    #        return [(move, self.make_move(move, state))
    #                for move in self.legal_moves(state)]

    def is_legal_position(self, row, column):
        """Checks if a specified position is legal"""
        return 0 <= row < self.height and 0 <= column < self.width

    def __repr__(self):
        return '<%s>' % self.__class__.__name__

''' ============================================='''

"""Othello, built on Norvig's Game class

"""

from utils import *
from tkinter import *
import random, re, time

# from myothello import boardstate_utility_fn, alphabeta_parameters

# give names to the internal piece value representations
Empty = 0
Black = 1
White = 2
Outer = 3


def calc_all_squares():
    """Function to calculate the array references for all valid board squares."""
    result = []
    for x in range(18, 271):
        y = x % 17
        if 1 <= y and y <= 15:
            result.append(x)
    # final = tuple(result)
    final = result
    return final


All_Squares = calc_all_squares()
All_Directions = [-18, -17, -16, -1, 1, 16, 17, 18]
BigInitialValue = 1000000

# Constants for graphics
GridSize = 25  # size in pixels of each square on playing board
PieceSize = GridSize - 8  # size in pixels of each playing piece
Offset = 2  # offset in pixels of board from edge of canvas
BoardColor = '#cccccc'  # color of board - medium green
HiliteColor = '#cffffc'  # color of highlighted square - light green
PlayerColors = ('', '#FFFD1B', '#0102FF')  # rgb values for black, white
PlayerNames = ('', 'Black', 'White')  # Names of players as displayed to the user
MoveDelay = 1000  # pause 1000 msec (1 sec) between moves
fn_array = [None, None]  # array to hold user-defined functions


def opponent(player):
    """Return the opponent of player or None if player is not valid."""
    if player == White:
        return Black
    elif player == Black:
        return White
    else:
        return None


class Board:
    "Holds the Tk GUI and the current board state"

    class Square:
        "Holds data related to a square of the board"

        def __init__(self, x, y):
            self.x, self.y = x, y  # location of square (in range 0-7)
            self.ref = (x * 17) + y + 18  # location of square in internal board representation
            self.player = 0  # number of player occupying square
            self.squareId = 0  # canvas id of rectangle
            self.pieceId = 0  # canvas id of circle

    def __init__(self, game, strategies=(), initialTime=1800):
        '''Initialize the interactive game board.  An optional list of
           computer opponent strategies can be supplied which will be
           displayed in a menu to the user.
        '''

        self.game = game
        self.initialTime = initialTime
        self.passedTest = ''
        # create a Tk frame to hold the gui
        self._frame = Frame()
        # set the window title
        self._frame.master.wm_title('Pythello')
        # build the board on a Tk drawing canvas
        size = 18 * GridSize  # make room for 8x8 squares
        self._canvas = Canvas(self._frame, width=size, height=size)
        self._canvas.pack()
        # add button for starting game
        self._menuFrame = Frame(self._frame)
        self._menuFrame.pack(expand=Y, fill=X)
        self._newGameButton = Button(self._menuFrame, text='New Game', command=self._newGame)
        self._newGameButton.pack(side=LEFT, padx=5)
        Label(self._menuFrame).pack(side=LEFT, expand=Y, fill=X)
        # add menus for choosing player strategies
        self._strategies = {}  # strategies, indexed by name
        optionMenuArgs = [self._menuFrame, 0, 'Human']
        for s in strategies:
            name = s.name
            optionMenuArgs.append(name)
            self._strategies[name] = s
        self._strategyVars = [0]  # dummy entry so strategy indexes match player numbers
        # make an menu for each player
        for n in (1, 2):
            label = Label(self._menuFrame, anchor=E, text='%s:' % PlayerNames[n])
            label.pack(side=LEFT, padx=10)
            var = StringVar();
            var.set('Human')
            var.trace('w', self._strategyMenuCallback)
            self._strategyVars.append(var)
            optionMenuArgs[1] = var
            #            menu = apply(OptionMenu, optionMenuArgs)
            menu = OptionMenu(*optionMenuArgs)
            menu.pack(side=LEFT)
        # add a label for showing the status
        self._status = Label(self._frame, relief=SUNKEN, anchor=W)
        self._status.pack(expand=Y, fill=X)
        # map the frame in the main Tk window
        self._frame.pack()

        # track the board state
        self._squares = {}  # Squares indexed by (x,y)
        self._enabledSpaces = ()  # list of valid moves as returned by BoardState.getmoves()
        for x in range(15):
            for y in range(15):
                square = self._squares[x, y] = Board.Square(x, y)
                x0 = x * GridSize + Offset
                y0 = y * GridSize + Offset
                square.squareId = self._canvas.create_rectangle(x0, y0,
                                                                x0 + GridSize, y0 + GridSize,
                                                                fill=BoardColor)

        # _afterId tracks the current 'after' proc so it can be cancelled if needed
        self._afterId = 0

        # ready to go - start a new game!
        self._newGame()

    def play(self):
        'Play the game! (this is the only public method)'
        self._frame.mainloop()

    def _postStatus(self, text):
        # updates the status line text
        self._status['text'] = text

    def _strategyMenuCallback(self, *args):
        # this is called when one of the player strategies is changed.
        # _updateBoard will keep everything in sync
        p1 = self._strategies.get(self._strategyVars[1].get())
        p2 = self._strategies.get(self._strategyVars[2].get())

        self.clocks = {p1: self.initialTime, p2: self.initialTime}
        self._updateBoard()

    def _newGame(self):
        # delete existing pieces
        for s in self._squares.values():
            if s.pieceId:
                self._canvas.delete(s.pieceId)
                s.pieceId = 0
        # create a new board state and display it
        self._state = BoardState()

        # get the players to make it easier to reset the clocks
        p1 = self._strategies.get(self._strategyVars[1].get())
        p2 = self._strategies.get(self._strategyVars[2].get())
        # reset the timing clocks
        self.clocks = {p1: self.initialTime, p2: self.initialTime}

        self._updateBoard()

    def _updateBoard(self):
        # cancel 'after' proc, if any
        if self._afterId:
            self._frame.after_cancel(self._afterId)
            self._afterId = 0
        # reset any enabled spaces
        self._disableSpaces()
        # update canvas display to match current state
        for pos, player in self._state.getPieces().items():
            square = self._squares[pos]
            if square.pieceId:
                if square.player != player:
                    self._canvas.itemconfigure(square.pieceId, fill=PlayerColors[player])
            else:
                x, y = pos
                x0 = x * GridSize + Offset + 4
                y0 = y * GridSize + Offset + 4
                square.pieceId = self._canvas.create_oval(x0, y0,
                                                          x0 + PieceSize, y0 + PieceSize,
                                                          fill=PlayerColors[player])
        # prepare for next move, either human or ai
        player = self._state.getPlayer()
        moves = self._state.legal_moves()
        # check for game over
        if not moves:
            self._gameOver()
            return
        # check for a pass
        if len(moves) == 1 and moves[0] == None:
            # fix this later. . .
            # must pass - do it now
            ##            self._state = moves[0][2]
            ##            moves = self._state.getMoves()
            ##            if not moves:
            ##                self._gameOver()
            ##                return
            ##            # prepend status message with passed message
            # if we passed on the previous move too
            if self.passedText:
                self._gameOver()
                return
            self.passedText = PlayerNames[player] + ' must pass - '
            # update player
            player = self._state.getPlayer()
        else:
            # player can't pass
            self.passedText = ''

        # get strategy (if not human)
        ai = self._strategies.get(self._strategyVars[player].get())
        if ai:
            # ai: we have to schedule the ai to run
            self._postStatus(self.passedText + "%s (%s) (%s time left) is thinking" % \
                             (ai.name, PlayerNames[player], self.clocks[ai]))
            self._afterId = self._frame.after_idle(self._processAi, ai, moves)
        else:
            # human: just enable legal moves and wait for a click
            self._postStatus(self.passedText + PlayerNames[player] + "'s turn")
            self._enabledSpaces = self._state.getxyMoves()
            self._enableSpaces()

    def _processAi(self, ai, moves):
        # calls the strategy to determine next move
        if len(moves) == 1:
            # only one choice, don't both calling strategy
            self._state = self._state.make_move(moves[0])
        else:
            # self.game.calculate_utility = ai.calculate_utility
            # update the current_player as each player considers their move
            self.game.current_player = ai
            params = ai.alphabeta_parameters(self._state, self.clocks[ai])
            startTime = time.clock()
            move = alphabeta_search(self._state, self.game, params[0], params[1], params[2])
            endTime = time.clock()
            moveTime = endTime - startTime
            if moveTime > self.clocks[ai]:
                print("Player", ai.name, "took too much time and loses.")
                self._gameOver()
                return
            else:
                self.clocks[ai] -= moveTime

            # call strategy
            # move = ai(self.game, self._state)
            # x,y,boardstate = ai.getNextMove(self._state.getPlayer(), moves)
            self._state = self._state.make_move(move)
        self._afterId = self._frame.after(MoveDelay, self._updateBoard)

    def _enableSpaces(self):
        # make spaces active where a legal move is possible (only used for human players)
        for x, y in self._enabledSpaces:
            if x == -1: break
            id = self._squares[x, y].squareId
            self._canvas.tag_bind(id, '<ButtonPress>',
                                  lambda e, s=self, x=x, y=y: s._selectSpace(x, y))
            self._canvas.tag_bind(id, '<Enter>',
                                  lambda e, c=self._canvas, id=id: \
                                      c.itemconfigure(id, fill=HiliteColor))
            self._canvas.tag_bind(id, '<Leave>',
                                  lambda e, c=self._canvas, id=id: \
                                      c.itemconfigure(id, fill=BoardColor))

    def _disableSpaces(self):
        # remove event handlers for all enabled spaces
        for x, y in self._enabledSpaces:
            if x == -1: break
            id = self._squares[x, y].squareId
            self._canvas.tag_unbind(id, '<ButtonPress>')
            self._canvas.tag_unbind(id, '<Enter>')
            self._canvas.tag_unbind(id, '<Leave>')
            self._canvas.itemconfigure(id, fill=BoardColor)
        self._enabledSpaces = ()

    def _selectSpace(self, x, y):
        # this is called when a human clicks on a space to place a piece
        self._state = self._state.make_move(x * 17 + y + 18)
        self._updateBoard()

    def _gameOver(self):
        # the game is over.  Count up the pieces and declare the winner.
        count = [0, 0, 0]  # first entry is a dummy
        for player in self._state.getPieces().values():
            count[player] = count[player] + 1
        self._postStatus('Game Over,  %s: %d  -  %s: %d' % \
                         (PlayerNames[1], count[1], PlayerNames[2], count[2]))


def start_graphical_othello_game(p1, p2, initialTime=1800):
    strategies = (p1, p2)
    game = Game(SIZE,SIZE)
    p1.initialize(game.initial, initialTime, Black)
    p2.initialize(game.initial, initialTime, White)
    board = Board(game, strategies, initialTime)
    # board.initialTime = initialTime
    board.play()

start_graphical_othello_game(Player(), Player())

##play_gomoku(Player(), Player())