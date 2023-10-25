import datetime
import os
import sqlite3
import shutil

from pentamusic.basedatos.concert import Concert
from pentamusic.basedatos.session import Session
from pentamusic.basedatos.sheet import Sheet
from pentamusic.basedatos.user_sheet import UserSheet
from pentamusic.crypto import Crypto


class SQL:
    class __SQL:
        basepath = os.path.expanduser("~/PentaMusic")

        def __init__(self):
            self.initialize()

        def initialize(self):
            # Creamos base de datos
            if not os.path.exists(self.basepath):
                print("Creada carpeta del programa.")
                os.makedirs(self.basepath)
            self.con = sqlite3.connect(self.basepath + "/penta.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

            # Usado para poder ejecutar comandos sql
            self.c = self.con.cursor()

            # ============================================= Base de Datos =============================================

            # Tabla que almacena las cuentas de los usuarios
            self.c.execute("""CREATE TABLE IF NOT EXISTS accounts (
                                            user_id TEXT PRIMARY KEY,
                                            user_pwd BLOB NOT NULL,
                                            salt BLOB NOT NULL,
                                            salt_crypt BLOB NOT NULL
                        )""")

            # Tabla que almacena los conciertos de cada usuario
            self.c.execute("""CREATE TABLE IF NOT EXISTS concerts (
                                            user TEXT,
                                            title TEXT NOT NULL,
                                            date TIMESTAMP,
                                            place TEXT NOT NULL,
                                            PRIMARY KEY (user, date),
                                            FOREIGN KEY (user) REFERENCES accounts(user_id)
                        )""")

            # Tabla que almacena las partituras de los usuarios
            self.c.execute("""CREATE TABLE IF NOT EXISTS sheets (
                                            id TEXT PRIMARY KEY,
                                            title TEXT NOT NULL,
                                            owner TEXT NOT NULL,
                                            public NUMERIC,
                                            instrument TEXT, 
                                            composer TEXT,
                                            file_nonce BLOB,
                                            bars NUMERIC,
                                            CONSTRAINT CK_sheet_public CHECK (public IN (0, 1)),
                                            CONSTRAINT CK_sheet_bars CHECK (bars >= 0)
                        )""")

            # Tabla que relaciona cada partitura con su correspondiente usuario
            self.c.execute("""CREATE TABLE IF NOT EXISTS accounts_sheets (
                                                            user TEXT,
                                                            sheet TEXT,
                                                            comments BLOB,
                                                            comments_nonce BLOB,
                                                            learned_bar BLOB,
                                                            learned_bar_nonce BLOB,
                                                            PRIMARY KEY (user, sheet),
                                                            FOREIGN KEY (user) REFERENCES accounts(user_id),
                                                            FOREIGN KEY (sheet) REFERENCES sheets(id)
                                        )""")

            # Tabla que relaciona los conciertos con las partituras.
            self.c.execute("""CREATE TABLE IF NOT EXISTS concerts_sheets (
                                                            concert_user TEXT,
                                                            concert_date TIMESTAMP,
                                                            sheet TEXT,
                                                            PRIMARY KEY (concert_user, concert_date, sheet),
                                                            FOREIGN KEY (concert_user, concert_date) REFERENCES concerts(user, date) ON UPDATE CASCADE,
                                                            FOREIGN KEY (sheet) REFERENCES sheets(id)
                                        )""")

            # Disparador que provoca que antes de borrar una partitura, borra todas sus asociaciones con los usuarios
            self.c.execute("""CREATE TRIGGER IF NOT EXISTS delete_sheets
                                                        BEFORE DELETE ON sheets
                                                        FOR EACH ROW
                                                        BEGIN
                                                            DELETE FROM accounts_sheets WHERE sheet=OLD.id;
                                                            DELETE FROM concerts_sheets WHERE sheet=OLD.id;
                                                        END;
                                        """)
            self.c.execute("""CREATE TRIGGER IF NOT EXISTS delete_concert
                                                        BEFORE DELETE ON concerts
                                                        FOR EACH ROW
                                                        BEGIN
                                                            DELETE FROM concerts_sheets WHERE concert_user=OLD.user AND concert_date=OLD.date;
                                                        END;
                                        """)

            # Vista que muestra las partituras que han sido indicadas como publicas
            self.c.execute("""CREATE VIEW IF NOT EXISTS public_sheets AS SELECT * FROM sheets WHERE public = 1""")

        # -------------------------------------------- TABLA PARTITURAS ------------------------------------------------
        def insert_sheet(self, id, nombre_partitura, nombre_creador, publica, file_nonce, compositor=None, instrumento=None, bars=0):
            query = "INSERT INTO sheets (id, title, owner, public, composer, instrument, file_nonce, bars) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            values = (id, nombre_partitura, nombre_creador, publica, instrumento, compositor, file_nonce, bars)
            self.c.execute(query, values)
            self.con.commit()
            self.insert_usersheet(Session().user, id)

        def delete_sheet(self, sheet_id):
            query = "DELETE FROM sheets WHERE id=?"
            values = (sheet_id,)
            self.c.execute(query, values)
            self.con.commit()
            os.remove(self.basepath + "/Sheets/" + sheet_id + ".pdf")

        def update_sheet(self, id, nombre_partitura, nombre_creador, publica, file_nonce, compositor, instrumento, bars):
            query = "UPDATE sheets SET title=?,owner=?,public=?,composer=?,instrument=?,file_nonce=?,bars=? WHERE id=?"
            values = (nombre_partitura, nombre_creador, publica, compositor, instrumento, file_nonce, bars, id)
            self.c.execute(query, values)
            self.con.commit()

        def get_public_sheet(self):
            query = "SELECT * FROM sheets WHERE public = 1"
            self.c.execute(query)
            result = self.c.fetchall()

            sheets = []
            for row in result:
                sheets.append(Sheet(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
            return sheets

        def get_sheet(self, id: str) -> Sheet:
            query = "SELECT * FROM sheets WHERE id = ?"
            self.c.execute(query, (id,))

            result = self.c.fetchone()

            if result is not None:
                return Sheet(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7])

        # ------------------------------------------- TABLA ACCOUNTS_SHEET ---------------------------------------------
        def get_usersheet(self, user: str, sheet_id: str) -> UserSheet:
            query = "SELECT * FROM accounts_sheets WHERE user = ? AND sheet = ?"
            self.c.execute(query, (user, sheet_id))
            result = self.c.fetchone()
            if result is not None:
                decrypted_comments = Crypto().decrypt_data(result[2], result[3])
                decrypted_learned_bar = Crypto().decrypt_data(result[4], result[5])
                return UserSheet(result[0], self.get_sheet(result[1]), decrypted_comments, decrypted_learned_bar, result[3], result[5])

        def get_all_usersheets(self, owner: str):
            query = "SELECT * FROM accounts_sheets WHERE user = ?"
            self.c.execute(query, (owner,))
            result = self.c.fetchall()
            sheets = []
            for row in result:
                sheet = self.get_sheet(row[1])
                # las partituras solo se devuelven si son públicas o eres el dueño, si no estarán encriptadas y no se podrán ver
                if sheet.is_public == 1 or sheet.owner == owner:
                    decrypted_comments = Crypto().decrypt_data(row[2], row[3])
                    decrypted_learned_bar = Crypto().decrypt_data(row[4], row[5])
                    sheets.append(UserSheet(row[0], sheet, decrypted_comments, decrypted_learned_bar, row[3], row[5]))
            return sheets

        def insert_usersheet(self, user_id, sheet_id):
            query = "INSERT INTO accounts_sheets (user, sheet, comments, learned_bar, comments_nonce, learned_bar_nonce) VALUES (?, ?, ?, ?, ?, ?)"
            comments_nonce = os.urandom(12)
            learned_bar_nonce = os.urandom(12)
            values = (user_id, sheet_id, Crypto().encrypt_data("", comments_nonce), Crypto().encrypt_data(0, learned_bar_nonce), comments_nonce, learned_bar_nonce)
            self.c.execute(query, values)
            self.con.commit()

        def update_usersheet(self, sheet_id, user, comments, learned_bar: int, comments_nonce, learned_bar_nonce):
            query = "UPDATE accounts_sheets SET sheet=?,user=?,comments=?,learned_bar=?,comments_nonce=?,learned_bar_nonce=? WHERE sheet=? AND user=?"
            values = (sheet_id, user, Crypto().encrypt_data(comments, comments_nonce), Crypto().encrypt_data(learned_bar, learned_bar_nonce), comments_nonce, learned_bar_nonce, sheet_id, user)
            self.c.execute(query, values)
            self.con.commit()

        def delete_usersheet(self, sheet_id, user):
            query = "DELETE FROM accounts_sheets WHERE sheet=? AND user=?"
            values = (sheet_id, user)
            self.c.execute(query, values)
            self.con.commit()
            # si es el dueño de la partitura, entonces también borramos la partitura
            sheet = self.get_sheet(sheet_id)
            if sheet.owner == user:
                self.delete_sheet(sheet_id)

        # -------------------------------------------- TABLA CONCIERTO -------------------------------------------------
        def insert_concerts(self, user, title, date, place):
            query = "INSERT INTO concerts (user, title, date, place) VALUES (?, ?, ?, ?)"
            # Tupla con los valores a insertar
            values = (user, title, self.format_date(date), place)
            self.c.execute(query, values)
            self.con.commit()

        def format_date(self, date: datetime.datetime) -> str:
            f = '%Y-%m-%d %H:%M:%S'
            return date.strftime(f)

        def delete_concert(self, user, date):
            query = "DELETE FROM concerts WHERE user=? AND date=?"
            values = (user, self.format_date(date))
            self.c.execute(query, values)
            self.con.commit()

        def update_concert(self, user, title, date, place, original_date):
            query = "UPDATE concerts SET user=?,title=?,date=?,place=? WHERE user=? AND date=?"
            # Tupla con los valores a insertar
            values = (user, title, self.format_date(date), place, user, self.format_date(original_date))
            self.c.execute(query, values)
            self.con.commit()

        def get_concert(self, user, date) -> Concert:
            query = "SELECT * FROM concerts WHERE user = ? AND date = ?"
            self.c.execute(query, (user, self.format_date(date)))
            result = self.c.fetchone()

            if result is not None:
                return Concert(result[0], result[1], result[2], result[3])

        def get_user_concerts(self, user: str):
            query = "SELECT * FROM concerts WHERE user = ?"
            self.c.execute(query, (user,))
            result = self.c.fetchall()
            concerts = []
            for row in result:
                concerts.append(Concert(row[0], row[1], row[2], row[3]))
            return concerts

        # -------------------------------------- TABLA CONCERTS_SHEETS -------------------------------------------------
        # Obtenemos los conciertos de un determinado usuario
        def get_all_concertsheets(self, concert_user, concert_date) -> list:
            # Consulat de la tabla concerts_sheets
            query = "SELECT * FROM concerts_sheets WHERE concert_user = ? AND concert_date = ?"
            # Ejecucion de consulta con los valores
            self.c.execute(query, (concert_user, concert_date))

            # Obtenemos el resultado
            result = self.c.fetchall()

            # Pasamos a lista las partituras que pertenecen al concierto
            sheets = []
            for row in result:
                sheets.append(self.get_sheet(row[2]))
            return sheets

        def insert_concertsheets(self, concert_user, concert_date, sheet):
            query = "INSERT INTO concerts_sheets (concert_user, concert_date, sheet) VALUES (?, ?, ?)"
            values = (concert_user, concert_date, sheet)
            self.c.execute(query, values)
            self.con.commit()

        def delete_concertsheets(self, concert_user, concert_date, sheet) -> None:
            query = "DELETE FROM concerts_sheets WHERE concert_user=? AND concert_date=? AND sheet=?"
            values = (concert_user,concert_date, sheet)
            self.c.execute(query, values)
            self.con.commit()

        # ----------------------------------------- TABLA USUARIOS -----------------------------------------------------

        # Funcion que inserta en la tabla usuarios
        def insert_user(self, user: str, token: bytes, salt: bytes, salt_for_encryption: bytes) -> None:
            # Primero buscamos si ya ha sido registrado
            if not self.get_registration(user):
                # Insertamos
                query = "INSERT INTO accounts (user_id, user_pwd, salt, salt_crypt) VALUES (?, ?, ?, ?)"
                # Tupla con los valores a insertar
                values = (user, token, salt, salt_for_encryption)
                self.c.execute(query, values)
                # Guardamos los cambios
                self.con.commit()
            else:
                # En caso de que ya exista, salta una excepcion
                raise Exception("El usuario ya existe.")

        def update_user(self, user: str, token: bytes, salt: bytes, salt_for_encryption: bytes):
            query = "UPDATE accounts SET user_id=?,user_pwd=?,salt=?,salt_crypt=? WHERE user_id=?"
            # Tupla con los valores a insertar
            values = (user, token, salt, salt_for_encryption, user)
            self.c.execute(query, values)
            self.con.commit()

        # Busqueda de usuarios
        def get_registration(self, user: str) -> bool:
            # Consulta de busqueda
            query = "SELECT * FROM accounts WHERE user_id = ?"
            # Ejecucion de consulta
            self.c.execute(query, (user,))

            # Recuperamos los resultados de la consulta
            result = self.c.fetchone()

            # Si result es None, significa que no se encontró en la tabla
            if result is None:
                return False
            else:
                return True

        def get_user_data(self, user: str, data_index) -> bytes:
            query = "SELECT * FROM accounts WHERE user_id = ?"
            self.c.execute(query, (user,))

            # Recuperamos los resultados de la consulta
            result = self.c.fetchone()

            # Si result es None, significa que no se encontró en la tabla
            if result is None:
                raise Exception("El usuario no se encuentra en la base de datos.")
            else:
                return result[data_index]


        # ----------------------------------------------------- GENERAL ------------------------------------------------

        # Permite cerrar la base de datos
        def close(self):
            # Guardamos los cambios hechos
            self.con.commit()

            # Cerramos la conexión a la base de datos
            self.con.close()

        # Funcion que permite resetear la base de datos.
        def reset(self):
            # cerramos la conexión
            self.close()
            # ahora borramos los archivos
            shutil.rmtree(self.basepath)
            print("Datos borrados.")
            # y recreamos la base de datos
            self.initialize()

    # Singleton para tener una única instancia de esta clase
    instance = None

    def __new__(cls):
        if not SQL.instance:
            SQL.instance = SQL.__SQL()
        return SQL.instance

    def __getattr__(self, item):
        return getattr(self.instance, item)

    def __setattr__(self, key, value):
        return setattr(self.instance, key, value)