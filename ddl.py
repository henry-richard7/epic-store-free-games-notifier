import sqlite3


def create_table():
    sqlite_db = "games.db"
    conn = sqlite3.connect(sqlite_db)
    conn.execute("""
    CREATE TABLE alerted_games
    (
    game_name Text
    )
    """)
    conn.close()

def truncate_table():
    sqlite_db = "games.db"
    conn = sqlite3.connect(sqlite_db)
    query = "Truncate TABLE alerted_games"
    conn.execute(query)
    conn.commit()
    conn.close()

def insert_query(game_name):
    sqlite_db = "games.db"
    conn = sqlite3.connect(sqlite_db)
    query = f'''
    INSERT INTO alerted_games (game_name) VALUES ("{game_name}")
    '''
    conn.execute(query)
    conn.commit()
    conn.close()


def get_alerted_games():
    sqlite_db = "games.db"
    conn = sqlite3.connect(sqlite_db)
    query = "SELECT game_name FROM alerted_games"
    result = conn.execute(query)
    games = []
    for game in result:
        games.append(game[0])
    return games
