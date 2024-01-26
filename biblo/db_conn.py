import sqlite3
import logging

logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)

class DBConn():
    def __init__(self) -> None:
        self.db_conn = sqlite3.connect("D:/MSCS/Q2/CA/CA_emotion_facial_recognition_new/sql_database/users.db")
        self.cur = self.db_conn.cursor()
    
    def db_create_and_insert_dummy(self):    
        self.cur.execute("""CREATE TABLE IF NOT EXISTS users (
            userid INTEGER PRIMARY KEY, 
            name TEXT, 
            current_user BOOLEAN,
            emotion TEXT
            );""")
        self.cur.execute("INSERT INTO users VALUES (2, 'PLACEHOLDER', 0, 'HAPPY')")
        logger.info("Successfully created and inserted")
        return

    
    def fetch_current_user(self):
        res = self.cur.execute("SELECT userid, name, emotion, current_user FROM users WHERE current_user = 1").fetchall()[0]
        if res[1] == 'PLACEHOLDER':
            new_user = True
        else:
            new_user = False
        logger.info("Fetched user: ",str(res))
        return res, new_user

    def update_name(self, user_id, name):
        self.cur.execute(f"UPDATE users SET name = '{name}' WHERE userid = {user_id};")
        self.db_conn.commit()
        logger.info("Updated name")
        return 

    def fetch_emotion(self, user_id):
        res = self.cur.execute(f"SELECT emotion FROM users WHERE userid = {user_id}").fetchall()[0]
        logger.info("Fetched user emotion: ",str(res))
        return res[0]
    
    def exit_user(self, user_id):
        if user_id:
            self.cur.execute(f"UPDATE users SET current_user = 0 WHERE userid = {user_id};")
            self.db_conn.commit()
            return

    def fetch_all(self):
        res = self.cur.execute(f"SELECT * FROM users").fetchall()
        return(res)

    def close_connection(self):
        self.db_conn.commit()
        self.db_conn.close()        
        logger.info("Connection closed...")

if __name__ == '__main__':
    conn = DBConn()
    # conn.db_create_and_insert_dummy()
    # res, new_user = conn.fetch_current_user()
    res = conn.fetch_all()
    print(res)
    # print(new_user)
    # conn.fetch_emotion(1)
    # conn.exit_user(1)
    # conn.update_name(1,"Bob")
    # res, new_user = conn.fetch_current_user()
    # print(res)
    # print(new_user)
    conn.close_connection()
    