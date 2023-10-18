import datetime
import os
import sqlite3
import shutil

from pentamusic.basedatos.concert import Concert
from pentamusic.basedatos.sheet import Sheet
from pentamusic.basedatos.user_sheet import UserSheet


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
            self.con = sqlite3.connect(self.basepath + "/penta.db", detect_types = sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

            # Esto lo usaremos para poder ejecutar comandos SQL
            self.c = self.con.cursor()

            # Creamos nuestra base de datos
            self.c.execute("""CREATE TABLE IF NOT EXISTS accounts (
                                            user_id TEXT PRIMARY KEY,
                                            user_pwd BLOB NOT NULL,
                                            salt BLOB NOT NULL
                        )""")
            self.c.execute("""CREATE TABLE IF NOT EXISTS concerts (
                                            user TEXT,
                                            title TEXT NOT NULL,
                                            date TIMESTAMP,
                                            place TEXT NOT NULL,
                                            PRIMARY KEY (user, date),
                                            FOREIGN KEY (user) REFERENCES accounts(user_id)
                        )""")
            self.c.execute("""CREATE TABLE IF NOT EXISTS sheets (
                                            id TEXT PRIMARY KEY,
                                            title TEXT NOT NULL,
                                            owner TEXT NOT NULL,
                                            public NUMERIC,
                                            instrument TEXT, 
                                            composer TEXT,
                                            CONSTRAINT CK_sheet_public CHECK (public IN (0, 1))
                        )""")
            self.c.execute("""CREATE TABLE IF NOT EXISTS accounts_sheets (
                                                            user TEXT,
                                                            sheet TEXT,
                                                            comments TEXT,
                                                            learned_bar NUMERIC,
                                                            PRIMARY KEY (user, sheet),
                                                            FOREIGN KEY (user) REFERENCES accounts(user_id),
                                                            FOREIGN KEY (sheet) REFERENCES sheets(id)
                                        )""")
            self.c.execute("""CREATE TABLE IF NOT EXISTS concerts_sheets (
                                                            concert_user TEXT,
                                                            concert_date TIMESTAMP,
                                                            sheet TEXT,
                                                            PRIMARY KEY (concert_user, concert_date, sheet),
                                                            FOREIGN KEY (concert_user, concert_date) REFERENCES concerts(user, date) ON UPDATE CASCADE,
                                                            FOREIGN KEY (sheet) REFERENCES sheets(id)
                                        )""")
            # antes de insertar una partitura, creamos una asociación con el usuario actual
            self.c.execute("""CREATE TRIGGER IF NOT EXISTS insert_sheets
                                                        AFTER INSERT ON sheets
                                                        FOR EACH ROW
                                                        BEGIN
                                                            INSERT INTO accounts_sheets VALUES (NEW.owner, NEW.id, NULL, 0);
                                                        END;
                                        """)
            # antes de borrar una partitura, borramos todas sus asociaciones con los usuarios
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

            self.c.execute("""CREATE VIEW IF NOT EXISTS public_sheets AS SELECT * FROM sheets WHERE public = 1""")

        # -------------------------------------------- TABLA PARTITURAS ------------------------------------------------
        def insertar_partituras(self, id, nombre_partitura, nombre_creador, publica, compositor=None, instrumento=None):
            query = "INSERT INTO sheets (id, title, owner, public, composer, instrument) VALUES (?, ?, ?, ?, ?, ?)"
            values = (id, nombre_partitura, nombre_creador, publica, instrumento, compositor)
            self.c.execute(query, values)
            self.con.commit()

        def delete_partitura(self, sheet_id):
            query = "DELETE FROM sheets WHERE id=?"
            values = (sheet_id,)
            self.c.execute(query, values)
            self.con.commit()
            os.remove(self.basepath + "/Sheets/" + sheet_id + ".pdf")

        def actualizar_partituras(self, id, nombre_partitura, nombre_creador, publica, compositor, instrumento):
            query = "UPDATE sheets SET title=?,owner=?,public=?,composer=?,instrument=? WHERE id=?"
            values = (nombre_partitura, nombre_creador, publica, compositor, instrumento, id)
            self.c.execute(query, values)
            self.con.commit()

        def get_partituras_publicas(self):
            query = "SELECT * FROM sheets WHERE public = 1"
            self.c.execute(query)
            result = self.c.fetchall()

            sheets = []
            for row in result:
                sheets.append(Sheet(row[0], row[1], row[2], row[3], row[4], row[5]))
            return sheets

        def get_partitura(self, id: str) -> Sheet:
            query = "SELECT * FROM sheets WHERE id = ?"
            self.c.execute(query, (id,))

            result = self.c.fetchone()

            if result is not None:
                return Sheet(result[0], result[1], result[2], result[3], result[4], result[5])

        # ------------------------------------------- TABLA ACCOUNTS_SHEET ---------------------------------------------
        def get_usersheet(self, user: str, sheet_id: str) -> UserSheet:
            query = "SELECT * FROM accounts_sheets WHERE user = ? AND sheet = ?"
            self.c.execute(query, (user, sheet_id))
            result = self.c.fetchone()
            if result is not None:
                return UserSheet(result[0], self.get_partitura(result[1]), result[2], result[3])

        def get_all_usersheets(self, owner: str):
            query = "SELECT * FROM accounts_sheets WHERE user = ?"
            self.c.execute(query, (owner,))
            result = self.c.fetchall()
            sheets = []
            for row in result:
                sheets.append(UserSheet(row[0], self.get_partitura(row[1]), row[2], row[3]))
            return sheets

        def insertar_usersheet(self, user_id, sheet_id):
            query = "INSERT INTO accounts_sheets (user, sheet, comments, learned_bar) VALUES (?, ?, ?, 0)"
            values = (user_id, sheet_id, None)
            self.c.execute(query, values)
            self.con.commit()

        def actualizar_usersheet(self, sheet_id, user, comments, learned_bar: int):
            query = "UPDATE accounts_sheets SET sheet=?,user=?,comments=?,learned_bar=? WHERE sheet=? AND user=?"
            values = (sheet_id, user, comments, learned_bar, sheet_id, user)
            self.c.execute(query, values)
            self.con.commit()

        def delete_usersheet(self, sheet_id, user):
            query = "DELETE FROM accounts_sheets WHERE sheet=? AND user=?"
            values = (sheet_id, user)
            self.c.execute(query, values)
            self.con.commit()
            # si es el dueño de la partitura, entonces también borramos la partitura
            sheet = self.get_partitura(sheet_id)
            if sheet.owner == user:
                self.delete_partitura(sheet_id)

        # -------------------------------------------- TABLA CONCIERTO -------------------------------------------------
        def insertar_concerts(self, user, title, date, place):
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
        def get_all_concertsheets(self, concert_user, concert_date):
            query = "SELECT * FROM concerts_sheets WHERE concert_user = ? AND concert_date = ?"
            self.c.execute(query, (concert_user, concert_date))
            result = self.c.fetchall()
            sheets = []
            for row in result:
                sheets.append(self.get_partitura(row[2]))
            return sheets

        def insertar_concertsheets(self, concert_user, concert_date, sheet):
            query = "INSERT INTO concerts_sheets (concert_user, concert_date, sheet) VALUES (?, ?, ?)"
            values = (concert_user, concert_date, sheet)
            self.c.execute(query, values)
            self.con.commit()

        def delete_concertsheets(self, concert_user, concert_date, sheet):
            query = "DELETE FROM concerts_sheets WHERE concert_user=? AND concert_date=? AND sheet=?"
            values = (concert_user,concert_date, sheet)
            self.c.execute(query, values)
            self.con.commit()

        # ----------------------------------------- TABLA USUARIOS -----------------------------------------------------
        def insertar_usuario(self, user: str, token: bytes, salt: bytes) -> None:
            # Ahora insertamos elementos
            if not self.consultar_registro(user):
                query = "INSERT INTO accounts (user_id, user_pwd, salt) VALUES (?, ?, ?)"
                # Tupla con los valores a insertar
                values = (user, token, salt)
                self.c.execute(query, values)
                self.con.commit()
            else:
                raise Exception("El usuario ya existe.")

        def consultar_registro(self, user):
            query = "SELECT * FROM accounts WHERE user_id = ?"
            self.c.execute(query, (user,))

            # Recuperamos los resultados de la consulta
            result = self.c.fetchone()

            # Si result es None, significa que no se encontró en la tabla
            if result is None:
                return False
            else:
                return True

        def consultar_dato_usuario(self, user, data_index) -> bytes:
            query = "SELECT * FROM accounts WHERE user_id = ?"
            self.c.execute(query, (user,))

            # Recuperamos los resultados de la consulta
            result = self.c.fetchone()

            # Si result es None, significa que no se encontró en la tabla
            if result is None:
                raise Exception("El usuario no se encuentra en la base de datos.")
            else:
                return result[data_index]


        # ------------------------------------------------ GENERAL ----------------------------------------------
        # Se usa para cerrar la base de datos
        def cerrar(self):
            # Guardamos los cambios hechos
            self.con.commit()

            # Cerramos la conexión a la base de datos. Buena práctica
            self.con.close()

        def reset(self):
            # cerramos la conexión
            self.cerrar()
            # ahora borramos los archivos
            shutil.rmtree(self.basepath)
            print("Datos borrados.")
            # y recreamos la base de datos
            self.initialize()

    # Usamos un singleton
    instance = None

    def __new__(cls):
        if not SQL.instance:
            SQL.instance = SQL.__SQL()
        return SQL.instance

    def __getattr__(self, item):
        return getattr(self.instance, item)

    def __setattr__(self, key, value):
        return setattr(self.instance, key, value)