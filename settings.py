import pygame
import time
from environment import Board
from environment import opponent_color


class settings:

    def __init__(self, black_piece=None, white_piece=None, interface=True, dir_save=None):
        
        #pieces
        self.black_piece = black_piece
        self.white_piece = white_piece

        #BLACK always has the first move on the center of the board.
        self.board = Board(next_color='BLACK')

        #interface
        interface = interface if black_piece and white_piece else True
        self.interface = Interface() if interface else None
        self.dir_save = dir_save

        # Metadata
        #self.time_elapsed = None
    
    #Who is the winner?
    #@property
    def winner(self):
        return self.board.winner

    #Who is the next player?
    #@property
    def next_player(self):
        return self.board.next_player

    #How many moves have been played?
    #@property
    def count_moves(self):
        return self.board.count_moves

    #Start the game with interface?
    def start(self):
        if self.interface:
            self._start_with_interface()
        else:
            self._start_without_interface()
    
    def _start_with_interface(self):

        """
        Start the game with Interface.

        """
        self.interface.initialize()
        self.time_elapsed = time.time()

        # First move is fixed on the center of board
        first_move = (10, 10)
        self.board.put_stone(first_move, check_legal=False)
        self.interface.draw(first_move, opponent_color(self.board.next_player))

        # Take turns to play move
        while self.board.winner is None:
            if self.board.next_player == 'BLACK':
                point = self.perform_one_move(self.black_piece)
            else:
                point = self.perform_one_move(self.white_piece)

            # Check if action is legal
            if point not in self.board.legal_actions:
                raise ValueError('Illegal action: %s' % str(point))

            # Save board image
            if self.dir_save:
                self.interface.save_image(self.dir_save)

        self.time_elapsed = time.time() - self.time_elapsed
        pygame.quit()

    def _start_without_interface(self):

        """
        Start the game without GUI.

        """

        self.time_elapsed = time.time()

        # First move is fixed on the center of board
        first_move = (10, 10)
        self.board.put_stone(first_move, check_legal=False)

        # Take turns to play move
        while self.board.winner is None:
            if self.board.next_player == 'BLACK':
                point = self.perform_one_move(self.black_piece)
            else:
                point = self.perform_one_move(self.white_piece)

            # Check if action is legal
            if point not in self.board.legal_actions:
                raise ValueError('Illegal action: %s' % str(point))

        self.time_elapsed = time.time() - self.time_elapsed

