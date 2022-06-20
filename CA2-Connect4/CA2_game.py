import math
from os import posix_spawn
from random import random
import random as rand
import copy
from turtle import pos
import timeit

PLAYER = 1
DEPTH = 7
AI = -1
NUMBER_OF_RUNS = 3
BOARD_SIZE = 2


class ConnectSin:
    YOU = 1
    CPU = -1
    EMPTY = 0
    DRAW = 0
    __CONNECT_NUMBER = 4
    board = None

    def __init__(self, board_size=(6, 7), silent=False):
        """
        The main class for the connect4 game

        Inputs
        ----------
        board_size : a tuple representing the board size in format: (rows, columns)
        silent     : whether the game prints outputs or not
        """
        assert len(board_size) == 2, "board size should be a 1*2 tuple"
        assert board_size[0] > 4 and board_size[1] > 4, "board size should be at least 5*5"

        self.columns = board_size[1]
        self.rows = board_size[0]
        self.silent = silent
        self.board_size = self.rows * self.columns

    def run(self, starter=None):
        """
        runs the game!

        Inputs
        ----------
        starter : either -1,1 or None. -1 if cpu starts the game, 1 if you start the game. None if you want the starter
            to be assigned randomly 

        Output
        ----------
        (int) either 1,0,-1. 1 meaning you have won, -1 meaning the player has won and 0 means that the game has drawn
        """
        if (not starter):
            starter = self.__get_random_starter()
        assert starter in [self.YOU, self.CPU], "starter value can only be 1,-1 or None"
        
        self.__init_board()
        turns_played = 0
        current_player = starter
        while(turns_played < self.board_size):
            
            if (current_player == self.YOU):
                self.__print_board()
                player_input = self.get_your_input()
            elif (current_player == self.CPU):
                player_input = self.__get_cpu_input()
            else:
                raise Exception("A problem has happend! contact no one, there is no fix!")
            if (not self.register_input(player_input, current_player)):
                self.__print("this move is invalid!")
                continue
            current_player = self.__change_turn(current_player)
            potential_winner = self.check_for_winners()
            turns_played += 1
            if (potential_winner != 0):
                self.__print_board()
                self.__print_winner_message(potential_winner)
                return potential_winner
        self.__print_board()
        self.__print("The game has ended in a draw!")
        return self.DRAW

    def get_your_input(self):
        """
        gets your input

        Output
        ----------
        (int) an integer between 1 and column count. the column to put a piece in
        """

        #return self.minimax(depth = DEPTH, isMaximizing=True)[0]
        return self.alphabeta(depth = DEPTH, alpha=-math.inf, beta=math.inf, isMaximizing=True)[0]

    def check_for_winners(self):
        """
        checks if anyone has won in this position

        Output
        ----------
        (int) either 1,0,-1. 1 meaning you have won, -1 meaning the player has won and 0 means that nothing has happened
        """
        have_you_won = self.check_if_player_has_won(self.YOU)
        if have_you_won:
            return self.YOU
        has_cpu_won = self.check_if_player_has_won(self.CPU)
        if has_cpu_won:
            return self.CPU
        return self.EMPTY

    def check_if_player_has_won(self, player_id):
        """
        checks if player with player_id has won

        Inputs
        ----------
        player_id : the id for the player to check

        Output
        ----------
        (boolean) true if the player has won in this position
        """
        return (
            self.__has_player_won_diagonally(player_id)
            or self.__has_player_won_horizentally(player_id)
            or self.__has_player_won_vertically(player_id)
        )
    
    def is_move_valid(self, move):
        """
        checks if this move can be played

        Inputs
        ----------
        move : the column to place a piece in, in range [1, column count]

        Output
        ----------
        (boolean) true if the move can be played
        """
        if (move < 1 or move > self.columns):
            return False
        column_index = move - 1
        return self.board[0][column_index] == 0
    
    def get_possible_moves(self):
        """
        returns a list of possible moves for the next move

        Output
        ----------
        (list) a list of numbers of columns that a piece can be placed in
        """
        possible_moves = []
        for i in range(self.columns):
            move = i + 1
            if (self.is_move_valid(move)):
                possible_moves.append(move)
        return possible_moves
    
    def register_input(self, player_input, current_player):
        """
        registers move to board, remember that this function changes the board

        Inputs
        ----------
        player_input : the column to place a piece in, in range [1, column count]
        current_player: ID of the current player, either self.YOU or self.CPU

        """
        if (not self.is_move_valid(player_input)):
            return False
        self.__drop_piece_in_column(player_input, current_player)
        return True

    def __init_board(self):
        self.board = []
        for i in range(self.rows):
            self.board.append([self.EMPTY] * self.columns)

    def __print(self, message: str):
        if not self.silent:
            print(message)

    def __has_player_won_horizentally(self, player_id):
        for i in range(self.rows):
            for j in range(self.columns - self.__CONNECT_NUMBER + 1):
                has_won = True
                for x in range(self.__CONNECT_NUMBER):
                    if self.board[i][j + x] != player_id:
                        has_won = False
                        break
                if has_won:
                    return True
        return False

    def __has_player_won_vertically(self, player_id):
        for i in range(self.rows - self.__CONNECT_NUMBER + 1):
            for j in range(self.columns):
                has_won = True
                for x in range(self.__CONNECT_NUMBER):
                    if self.board[i + x][j] != player_id:
                        has_won = False
                        break
                if has_won:
                    return True
        return False

    def __has_player_won_diagonally(self, player_id):
        for i in range(self.rows - self.__CONNECT_NUMBER + 1):
            for j in range(self.columns - self.__CONNECT_NUMBER + 1):
                has_won = True
                for x in range(self.__CONNECT_NUMBER):
                    if self.board[i + x][j + x] != player_id:
                        has_won = False
                        break
                if has_won:
                    return True
                has_won = True
                for x in range(self.__CONNECT_NUMBER):
                    if self.board[i + self.__CONNECT_NUMBER - 1 - x][j + x] != player_id:
                        has_won = False
                        break
                if has_won:
                    return True
        return False

    def __get_random_starter(self):
        players = [self.YOU, self.CPU]
        return players[int(random() * len(players))]
    
    def __get_cpu_input(self):
        """
        This is where clean code goes to die.
        """
        bb = copy.deepcopy(self.board)
        pm = self.get_possible_moves()
        for m in pm:
            self.register_input(m, self.CPU)
            if (self.check_if_player_has_won(self.CPU)):
                self.board = bb
                return m
            self.board = copy.deepcopy(bb)
        if (self.is_move_valid((self.columns // 2) + 1)):
            c = 0
            cl = (self.columns // 2) + 1
            for x in range(self.rows):
                if (self.board[x][cl] == self.CPU):
                    c += 1
            if (random() < 0.65):
                return cl
        return pm[int(random() * len(pm))]
    
    def __drop_piece_in_column(self, move, current_player):
        last_empty_space = 0
        column_index = move - 1
        for i in range(self.rows):
            if (self.board[i][column_index] == 0):
                last_empty_space = i
        self.board[last_empty_space][column_index] = current_player
        return True
        
    def __print_winner_message(self, winner):
        if (winner == self.YOU):
            self.__print("congrats! you have won!")
        else:
            self.__print("gg. CPU has won!")
    
    def __change_turn(self, turn):
        if (turn == self.YOU): 
            return self.CPU
        else:
            return self.YOU

    def __print_board(self):
        if (self.silent): return
        print("Y: you, C: CPU")
        for i in range(self.rows):
            for j in range(self.columns):
                house_char = "O"
                if (self.board[i][j] == self.YOU):
                    house_char = "Y"
                elif (self.board[i][j] == self.CPU):
                    house_char = "C"
                    
                print(f"{house_char}", end=" ")
            print()
    
    def calculate_heuristic(self, piece):
        heuristic = 0
        board = None
        #Horizontal
        for r in range(self.rows):
            row_cells = [self.board[r][c] for c in range(self.columns)]
            for c in range(self.columns - self.__CONNECT_NUMBER - 1):
                check_window = row_cells[c:c+self.__CONNECT_NUMBER]
                heuristic += self.get_window_value(piece, check_window)
                

        #Vertical
        for c in range(self.columns):
            col_cells = [self.board[r][c] for r in range(self.rows)]
            for r in range(self.rows - self.__CONNECT_NUMBER - 1):
                check_window = col_cells[r:r+self.__CONNECT_NUMBER]
                heuristic += self.get_window_value(piece, check_window)
        
        #DIAGONAL UP_RIGHT
        for r in range(self.rows - 3):
            for c in range(self.columns - 3):
                check_window = [self.board[r+i][c+i] for i in range(self.__CONNECT_NUMBER)]
                heuristic += self.get_window_value(piece, check_window)
        #Diagonal down right
        for r in range(self.__CONNECT_NUMBER-1, self.rows):
            for c in range(self.columns-(self.__CONNECT_NUMBER-1)):
                check_window = [self.board[r-i][c+i] for i in range(self.__CONNECT_NUMBER)]
                heuristic += self.get_window_value(piece, check_window)
        center_column = [self.board[r][self.columns//2] for r in range(self.rows)]
        heuristic += center_column.count(piece) * 5

        return heuristic

    def get_window_value(self, piece, window):
        value = 0
        enemy_piece  = piece
        if piece == self.YOU:
            enemy_piece = self.CPU
        else:
            enemy_piece = self.YOU
        if window.count(piece) == self.__CONNECT_NUMBER:
            value += 100
        elif window.count(piece) == 3 & window.count(self.EMPTY) == 1:
            value += 5
        elif window.count(piece) == 2 & window.count(self.EMPTY) == 2:
            value += 2
        
        if window.count(enemy_piece) == 3 & window.count(self.EMPTY) == 1:
            value -= 4
        
        return value
    def drop_piece_in_column(self, move, current_player):
        last_empty_space = self.get_last_empty_space(move)
        self.board[last_empty_space][move-1] = current_player

    def get_last_empty_space(self, move):
        last_empty_space = 0
        column_index = move - 1
        for i in range(self.rows):
            if (self.board[i][column_index] == 0):
                last_empty_space = i
        return last_empty_space
    
    def remove_first_piece_from_column(self, move):
        for i in range(self.rows):
            if self.board[i][move - 1] != self.EMPTY:
                self.board[i][move - 1] = self.EMPTY
                return

    def get_best_move_player(self):
        possible_moves = self.get_possible_moves()
        best_move = 0
        best_value = -math.inf
        for move in possible_moves:
            temp_board = self.board.copy()
            self.drop_piece_in_column(move, temp_board, self.YOU)
            current_value = self.calculate_heuristic(self.YOU, temp_board, has_temp_board=True)
            self.remove_first_piece_from_column(move)
            if current_value > best_value:
                best_value = current_value
                best_move = move
        return best_move
    
    def is_terminal_node(self):
        return self.check_if_player_has_won(self.CPU) | self.check_if_player_has_won(self.YOU) | len(self.get_possible_moves()) == 0

    def minimax(self, depth, isMaximizing):
        if self.is_terminal_node():
            if self.check_if_player_has_won(self.CPU):
                return (None, -100000000)
            elif self.check_if_player_has_won(self.YOU):
                return (None, 100000000)
            else:
                return (None, 0)
        elif depth == 0:
            return (None, self.calculate_heuristic(self.YOU))
        if isMaximizing:
            value = -math.inf 
            possible_moves = self.get_possible_moves()
            chosen_column = rand.choice(possible_moves)
            for move in possible_moves:
                self.drop_piece_in_column(move, self.YOU)
                state_value = self.minimax(depth-1, isMaximizing=False)
                self.remove_first_piece_from_column(move)
                if state_value[1] > value:
                    value = state_value[1]
                    chosen_column = move
            return chosen_column, value
        else:
            value = math.inf
            possible_moves = self.get_possible_moves()
            chosen_column = rand.choice(possible_moves)
            for move in possible_moves:
                self.drop_piece_in_column(move, self.CPU)
                state_value = self.minimax(depth-1, isMaximizing=True)
                self.remove_first_piece_from_column(move)
                if state_value[1] < value:
                    value = state_value[1]
                    chosen_column = move
            return chosen_column, value

    def alphabeta(self, depth, alpha, beta, isMaximizing):
        if self.is_terminal_node():
            if self.check_if_player_has_won(self.CPU):
                return (None, -math.inf)
            elif self.check_if_player_has_won(self.YOU):
                return (None, math.inf)
            else:
                return (None, 0)
        elif depth == 0:
            return (None, self.calculate_heuristic(self.YOU))

        if isMaximizing:
            value = -math.inf
            possible_moves = self.get_possible_moves()
            chosen_column = rand.choice(possible_moves)
            for move in possible_moves:
                self.drop_piece_in_column(move, self.YOU)
                state_value = self.alphabeta(depth-1, alpha, beta, isMaximizing=False)
                self.remove_first_piece_from_column(move)
                if state_value[1] > value:
                    value = state_value[1]
                    chosen_column = move
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return chosen_column, value
        else:
            value = math.inf
            possible_moves = self.get_possible_moves()
            chosen_column = rand.choice(possible_moves)
            for move in possible_moves:
                self.drop_piece_in_column(move, self.CPU)
                state_value = self.alphabeta(depth-1, alpha, beta, isMaximizing=True)
                self.remove_first_piece_from_column(move)
                if state_value[1] < value:
                    value = state_value[1]
                    chosen_column = move
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return chosen_column, value
player_wins = 0
average_runtime = 0
board_sizes = [(6,7), (7,8), (7,10)]

for i in range(NUMBER_OF_RUNS):
    start_time = timeit.default_timer()
    game = ConnectSin(board_size=board_sizes[BOARD_SIZE],silent=True)
    result = game.run()
    end_time = timeit.default_timer()
    average_runtime += end_time - start_time
    if result == PLAYER:
        player_wins += 1

average_runtime /= NUMBER_OF_RUNS
print("Normal minimax with depth {}:\nTime: {}\nWin Percentage: {}".format(DEPTH, average_runtime, player_wins/NUMBER_OF_RUNS))




        

