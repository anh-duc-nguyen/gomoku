from enum import Enum
from random import randint
from time import sleep


class Piece(Enum):
    """A piece on the board can be either empty, black, or white."""
    BLACK = 0
    WHITE = 1
    EMPTY = 2


class Player:
    def random_search(self, game):
        moves = game.legal_moves()
        return moves[randint(0, len(moves)-1)]

    # def alphabeta_full_search(self, game):



def play_gomoku(player0, player1):
    # Set-up logic
    players = (player0, player1)
    game = Game(5, 5)

    while True:
        for player in players:
            move = player.random_search(game)
            game.make_move(move)
            game.display()

            if game.terminal_test():
                print("Game over")
                return

            sleep(1)


class Game:
    """A game is similar to a problem, but it has a utility for each
    state and a terminal test instead of a path cost and a goal
    test. To create a game, subclass this class and implement
    legal_moves, make_move, utility, and terminal_test. You may
    override display and successors or you can inherit their default
    methods. You will also need to set the .initial attribute to the
    initial state; this can be done in the constructor."""

    def __init__(self, height, width):
        self.players = {True : 'X', False : 'O'}
        self.first_player = True 
        self.size = 15 
        self.height = height
        self.width = width
        self.cells = [[Piece.EMPTY for column in range(width)]
                      for row in range(height)]
        self.num_moves = 0
        self.last_move = (-1, -1)

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
        self.last_move = move

    # def utility(self, state, player):
    #     "Return the value of this final state to player."
    #     abstract()

    def terminal_test(self):
        if self.num_moves == self.height * self.width:
            return True

        directions = [[1, 0], [0, 1], [1, 1], [1, -1]]
        (row, col) = self.last_move
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

        if length != 5:
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
        symbols = ['X', 'O', '.']
        for row in range(self.height):
            for col in range(self.width):
                print(symbols[self.cells[row][col].value], end=' ')
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


#play_gomoku(Player(), Player())