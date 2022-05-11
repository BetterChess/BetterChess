import chess
import chess.engine
import chess.pgn
import math
import os
from matplotlib.pyplot import xcorr
import pandas as pd
from datetime import datetime
from extract import data_extract
from progress import simple_progress_bar


class ChessUser:
    def __init__(self, username, edepth, start_date):
        self.username = username
        self.edepth = edepth
        self.start_date = start_date
        self.file_paths = FileHandler(username=self.username)

    # def create_logger(self, filepath, name):
    #     logging.basicConfig(
    #         filename=filepath,
    #         format='[%(levelname)s %(module)s] %(message)s',
    #         level=logging.INFO, datefmt='%Y/%m/%d %I:%M:%S')
    #     self.logger = logging.getLogger(name)
    #     return self.logger

    def create_engine(self):
        self.engine = chess.engine.SimpleEngine.popen_uci(
            self.file_paths.stockfish)
        return self.engine

    def run_analysis(self):
        data_extract(
            self.username,
            self.file_paths.pgn_data,
            self.file_paths.extractlogfile)
        self.analyse_user()
        self.export_analysis()

    def analyse_user(self):
        all_games_data = pd.read_csv(
            self.file_paths.pgn_data, delimiter="|",
            names=["url_date", "game_data"])
        tot_games = len(all_games_data["game_data"])
        print("Analysing users data: ")
        for game_num, chess_game in enumerate(all_games_data["game_data"]):
            simple_progress_bar(game_num, tot_games, 1)
            with open(self.file_paths.temp, "w") as temp_pgn:
                temp_pgn.write(str(chess_game.replace(" ; ", "\n")))
            game = ChessGame(self.username, self.edepth,
                             self.start_date, self.engine, game_num)
            game.analyse_game()

    def export_analysis(self):
        print("User analysis finished")


class ChessGame(ChessUser):
    def __init__(self, username, edepth, start_date, engine, game_num):
        super().__init__(username, edepth, start_date)
        self.engine = engine
        self.game_num = game_num

    def analyse_game(self):
        self.init_game()
        self.init_board()
        self.init_move_lists()
        game_headers = ChessGameHeaders(
            self.username,
            self.edepth,
            self.start_date,
            self.engine,
            self.game_num,
            self.chess_game)
        self.game_datetime = game_headers.collect_headers()["Game_datetime"]

        for move_num, move in enumerate(self.chess_game.mainline_moves()):
            chess_move = ChessMove(
                self.username,
                self.edepth,
                self.start_date,
                self.engine,
                self.game_num,
                self.board,
                move_num,
                self.game_datetime)
            chess_move.analyse_move(move)

    def init_game(self):
        self.chess_game_pgn = open(self.file_paths.temp)
        self.chess_game = chess.pgn.read_game(self.chess_game_pgn)
        return self.chess_game

    def init_board(self):
        self.board = self.chess_game.board()
        return self.board

    def init_move_lists(self):
        self.gm_best_mv = []
        self.gm_mv_num = []
        self.gm_mv = []
        self.mainline_eval = []
        self.best_move_eval = []
        self.move_eval_diff = []
        self.gm_mv_ac = []
        self.l_movetype = []


class ChessGameHeaders(ChessGame):
    def __init__(self, username, edepth, start_date,
                 engine, game_num, chess_game):
        ChessGame.__init__(self, username, edepth,
                           start_date, engine, game_num)
        self.chess_game = chess_game
        self.engine = engine

    def collect_headers(self):
        header_dict = {
            "Game_date": self.game_dt(self.chess_game),
            "Game_time": self.game_t(self.chess_game),
            "Game_datetime": self.game_dt_time(),
            "Time_control": self.time_control(self.chess_game),
            "Username": self.username,
            "User_Colour": self.user_colour(),
            "User_rating": self.rating_user(),
            "Opponent_rating": self.rating_opponent(),
            "User_winner": self.user_winr(),
            "White_player": self.player_white(self.chess_game),
            "Black_player": self.player_black(self.chess_game),
            "White_rating": self.rating_white(self.chess_game),
            "Black_rating": self.rating_black(self.chess_game),
            "Opening_class": self.opening_cls(self.chess_game),
            "Opening_name": self.opening_nm(self.chess_game),
            "Termination": self.game_termination(self.chess_game),
            "Win_draw_loss": self.win_draw_loss(self.chess_game)}
        return header_dict

    def time_control(self, chess_game):
        self.game_time_cont = chess_game.headers["TimeControl"]
        return self.game_time_cont

    def player_white(self, chess_game):
        self.white = chess_game.headers["White"]
        return self.white

    def player_black(self, chess_game):
        self.black = chess_game.headers["White"]
        return self.black

    def user_colour(self):
        white = self.player_white(self.chess_game)
        self.player = "White" if white == self.username else "Black"
        return self.player

    def rating_white(self, chess_game):
        self.ratingwhite = chess_game.headers["WhiteElo"]
        return self.ratingwhite

    def rating_black(self, chess_game):
        self.ratingblack = chess_game.headers["BlackElo"]
        return self.ratingblack

    def opening_cls(self, chess_game):
        try:
            self.opening_class = chess_game.headers["ECO"]
        except KeyError:
            self.opening_class = "000"
        return self.opening_class

    def opening_nm(self, chess_game):
        try:
            opening_name_raw = chess_game.headers["ECOUrl"]
        except KeyError:
            opening_name_raw = "/NA"
        opening_string = opening_name_raw.split("/")[-1]
        self.opening_name = str(opening_string.replace("-", " ").strip())
        return self.opening_name

    def game_termination(self, chess_game):
        self.white = chess_game.headers["White"]
        return self.white

    def rating_user(self):
        player = self.user_colour()
        rating_w = self.rating_white(self.chess_game)
        rating_b = self.rating_black(self.chess_game)
        self.user_rating = rating_w if player == "White" else rating_b
        return self.user_rating

    def rating_opponent(self):
        player = self.user_colour()
        rating_w = self.rating_white(self.chess_game)
        rating_b = self.rating_black(self.chess_game)
        self.opp_rating = rating_w if player == "White" else rating_b
        return self.opp_rating

    def win_draw_loss(self, chess_game):
        if chess_game.headers["Result"] == "1-0":
            self.end_type = "White"
        elif chess_game.headers["Result"] == "0-1":
            self.end_type = "Black"
        else:
            self.end_type = "Draw"
        return self.end_type

    def user_winr(self):
        winner = self.win_draw_loss(self.chess_game)
        player = self.user_colour()
        pww = (winner == "White" and player == "White")
        pbw = (winner == "Black" and player == "Black")
        pwl = (winner == "Black" and player == "White")
        pbl = (winner == "White" and player == "Black")
        if pww or pbw:
            self.user_winner = "Win"
        elif pwl or pbl:
            self.user_winner = "Loss"
        else:
            self.user_winner = "Draw"
        return self.user_winner

    def game_dt(self, chess_game):
        self.game_date = chess_game.headers["UTCDate"]
        return self.game_date

    def game_t(self, chess_game):
        self.game_time = chess_game.headers["UTCTime"]
        return self.game_time

    def game_dt_time(self):
        game_date = self.game_dt(self.chess_game)
        game_time = self.game_t(self.chess_game)
        game_date_time = f"{game_date} {game_time}"
        self.game_datetime = datetime.strptime(game_date_time, '%Y.%m.%d %H:%M:%S')
        return self.game_datetime


class ChessMove(ChessGame):
    def __init__(self, username, edepth, start_date,
                 engine, game_num, board, move_num, game_datetime):
        ChessGame.__init__(self, username, edepth,
                           start_date, engine, game_num)
        self.board = board
        self.engine = engine
        self.move_num = move_num
        self.game_datetime = game_datetime

    def analyse_move(self, move):
        """Analyses a users move and exports results to move_data.csv"""
        self.str_bm, self.eval_bm = self.best_move()
        self.str_ml, self.eval_ml = self.mainline_move(move)
        self.evaldiff = self.eval_delta(
            self.move_num, self.eval_bm, self.eval_ml)
        self.move_acc = self.move_accuracy(self.evaldiff)
        self.move_type = self.assign_move_type(self.move_acc)
        self.export_move_data()

    def mainline_move(self, move):
        """Returns the users move and its evaluation."""
        self.str_ml = str(move)
        self.board.push_san(self.str_ml)
        eval_ml_init = self.engine.analyse(
            self.board,
            chess.engine.Limit(depth=self.edepth),
            game=object())
        self.eval_ml = self.move_eval(eval_ml_init)
        return self.str_ml, self.eval_ml

    def best_move(self):
        """Returns the best move from the engine and its evaluation."""
        best_move = self.engine.play(
            self.board,
            chess.engine.Limit(depth=self.edepth),
            game=object())
        self.str_bm = str(best_move.move)
        self.board.push_san(self.str_bm)
        eval_bm_init = self.engine.analyse(
            self.board,
            chess.engine.Limit(depth=self.edepth),
            game=object())
        self.eval_bm = self.move_eval(eval_bm_init)
        self.board.pop()
        return self.str_bm, self.eval_bm

    def move_eval(self, move):
        '''Returns the evalaution of the move played.'''
        get_eval = str(move['score'].white())
        if "#" in get_eval:
            get_eval = get_eval[1:]
        else:
            get_eval = get_eval
        get_eval = int(get_eval)
        return get_eval

    def eval_delta(self, move_num, eval_bm, eval_ml):
        '''Returns the eval difference between the best and mainline move.'''
        if move_num % 2 == 0:
            eval_diff = round(abs(eval_bm - eval_ml), 3)
            return eval_diff
        else:
            eval_diff = round(abs(eval_ml - eval_bm), 3)
            return eval_diff

    def move_accuracy(self, eval_diff):
        '''Returns the move accuracy for a given move.'''
        m, v = 0, 1.5
        move_acc = round(math.exp(-0.00003*((eval_diff-m)/v)**2)*100, 1)
        return move_acc

    def assign_move_type(self, move_acc):
        '''Returns the move type for a given move.'''
        # best = 2, excellent = 1, good = 0,
        # inacc = -1, mistake = -2, blunder = -3, missed win = -4
        if move_acc == 100:
            move_type = 2
        elif 99.5 <= move_acc < 100:
            move_type = 1
        elif 87.5 <= move_acc < 99.5:
            move_type = 0
        elif 58.6 <= move_acc < 87.5:
            move_type = -1
        elif 30 <= move_acc < 58.6:
            move_type = -2
        elif 2 <= move_acc < 30:
            move_type = -3
        else:
            move_type = -4
        return move_type

    def export_move_data(self):
        move_df = pd.DataFrame({
            "Username": self.username,
            "Game_date": self.game_datetime,
            "edepth": self.edepth,
            "Game_number": self.game_num,
            "Move_number": self.move_num,
            "Move": self.str_ml,
            "Move_eval": self.eval_ml,
            "Best_move": self.str_bm,
            "Best_move_eval": self.eval_bm,
            "Move_eval_diff": self.evaldiff,
            "Move accuracy": self.move_acc,
            "Move_type": self.move_type,
            }, index=[0])
        move_df.to_csv(
            self.file_paths.move_data, mode='a',
            header=False, index=False)



    

class InputHandler:
    @staticmethod
    def get_inputs():
        username = input("Enter your username: ")
        edepth = input("Enter the engine depth: ")
        i_start_y = input("Enter the start year for analysis (e.g. 2020): ")
        i_start_m = input("Enter the start month for analysis (e.g. 01-12): ")
        i_start_datetime = (i_start_y + "-" + i_start_m + "-01" + " 00:00:00")
        start_date = datetime.strptime(i_start_datetime, "%Y-%m-%d %H:%M:%S")
        return {"username": username,
                "edepth": edepth,
                "start_date": start_date}


class FileHandler:
    def __init__(self, username):
        self.username = username
        self.dir = os.path.dirname(__file__)
        stockfish_path = r"../lib/stkfsh_14.1/stockfish_14.1_win_x64_avx2.exe"
        self.stockfish = os.path.join(self.dir, stockfish_path)
        self.gamelogfile = os.path.join(
            self.dir,
            rf"../logs/user_games/{self.username}_game.log")
        self.extractlogfile = os.path.join(
            self.dir,
            rf"../logs/user_extract/{self.username}_url_date.log")
        self.temp = os.path.join(self.dir, r"../data/temp.pgn")
        self.move_data = os.path.join(self.dir, r"../data/move_data.csv")
        self.game_data = os.path.join(self.dir, r"../data/game_data.csv")
        self.pgn_data = os.path.join(
            self.dir,
            rf"../data/pgn_data/{self.username}_pgn_data.csv")
