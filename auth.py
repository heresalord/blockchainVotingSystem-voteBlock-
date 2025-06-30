import sqlite3
from db_manager import VoterDatabase

voter_db = VoterDatabase()

def authenticate_user(npi, password):
    try:
        with sqlite3.connect(voter_db.database_file) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT npi, full_name, password, role FROM voters WHERE npi = ?", (npi,))
            user = cursor.fetchone()
        if user:
            decrypted_password = voter_db.decrypt(user[2])
            if decrypted_password == password:
                decrypted_full_name = voter_db.decrypt(user[1])
                decrypted_role = voter_db.decrypt(user[3])
                return {'npi': user[0], 'full_name': decrypted_full_name, 'role': decrypted_role}
        return None
    except sqlite3.Error as error:
        print("Error while connecting to SQLite database:", error)
        return None
