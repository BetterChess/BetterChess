CREATE TABLE game_data (
    Username TEXT,
    Game_date TEXT,
    Game_time_of_day TEXT,
    Game_weekday TEXT,
    Engine_depth SMALLINT,
    Game_number SMALLINT,
    Game_type TEXT,
    White_player TEXT,
    White_rating SMALLINT,
    Black_player TEXT,
    Black_rating SMALLINT,
    User_colour TEXT,
    User_rating SMALLINT,
    Opponent_rating SMALLINT,
    User_win_percent FLOAT,
    Opp_win_percent FLOAT,
    User_winner TEXT,
    Opening_name TEXT,
    Opening_class TEXT,
    Termination TEXT,
    End_type TEXT,
    Number_of_moves SMALLINT,
    Accuracy FLOAT,
    Opening_accuracy FLOAT,
    Mid_accuracy FLOAT,
    End_accuracy FLOAT,
    No_best SMALLINT,
    No_excellent SMALLINT,
    No_good SMALLINT,
    No_inaccuracy SMALLINT,
    No_mistake SMALLINT,
    No_blunder SMALLINT,
    No_missed_win SMALLINT,
    Improvement TEXT,
    User_castle_num SMALLINT,
    Opp_castle_num SMALLINT,
    User_castled SMALLINT,
    Opp_castled SMALLINT,
    User_castle_phase SMALLINT,
    Opp_castle_phase SMALLINT,
    Game_pgn TEXT
)