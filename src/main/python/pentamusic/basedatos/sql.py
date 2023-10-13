import os
import sqlite3
import shutil

from pentamusic.basedatos.sheet import Sheet

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
            self.con = sqlite3.connect(self.basepath + "/penta.db")

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
                                            date DATE,
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
                                                            sheet NUMERIC,
                                                            comments TEXT,
                                                            learned_bar NUMERIC,
                                                            PRIMARY KEY (user, sheet),
                                                            FOREIGN KEY (user) REFERENCES accounts(user_id),
                                                            FOREIGN KEY (sheet) REFERENCES sheets(id)
                                        )""")
            self.c.execute("""CREATE TRIGGER IF NOT EXISTS insert_sheets
                                                        AFTER INSERT ON sheets
                                                        FOR EACH ROW
                                                        BEGIN
                                                            INSERT INTO accounts_sheets VALUES (NEW.owner, NEW.id, NULL, 0);
                                                        END;
                                        """)
            self.c.execute("""CREATE VIEW IF NOT EXISTS public_sheets AS SELECT * FROM sheets WHERE public = 1""")

        # -------------------------------------------- TABLA PARTITURAS ------------------------------------------------
        def insertar_partituras(self, id, nombre_partitura, nombre_creador, publica, compositor=None, instrumento=None):
            query = "INSERT INTO sheets (id, title, owner, public, composer, instrument) VALUES (?, ?, ?, ?, ?, ?)"
            values = (id, nombre_partitura, nombre_creador, publica, instrumento, compositor)
            self.c.execute(query, values)
            self.con.commit()

        def insertar_partitura_publica(self, user_id, sheet_id):
            query = "INSERT INTO accounts_sheets (user, sheet) VALUES (?, ?)"
            values = (user_id, sheet_id)
            self.c.execute(query, values)
            self.con.commit()

        def actualizar_partituras(self, id, nombre_partitura, nombre_creador, publica, compositor, instrumento):
            query = "UPDATE sheets SET title=?,owner=?,public=?,composer=?,instrument=? WHERE id=?"
            values = (nombre_partitura, nombre_creador, publica, compositor, instrumento, id)
            self.c.execute(query, values)
            self.con.commit()

        def get_partituras_usuario(self, owner: str):
            query = "SELECT * FROM accounts_sheets WHERE user = ?"
            self.c.execute(query, (owner,))
            result = self.c.fetchall()

            sheets = []
            for row in result:
                sheets.append(self.get_partitura(row[1]))
            return sheets

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

        # -------------------------------------------- TABLA CONCIERTO -------------------------------------------------
        def insertar_concerts(self, user, title, data, place):
            query = "INSERT INTO concerts (user, title, data, place) VALUES (?, ?, ?, ?, ?, ?)"
            # Tupla con los valores a insertar
            values = (id, user, title, data, place)
            self.c.execute(query, values)
            self.con.commit()

        def update_concert(self):
            query = "UPDATE sheets SET title=?,owner=?,public=?,composer=?,instrument=? WHERE id=?"
            # Tupla con los valores a insertar
            # values = (nombre_partitura, nombre_creador, publica, compositor, instrumento, id)
            # self.c.execute(query, values)
            self.con.commit()
        def check_concerts(self, user: str, date) -> Sheet:
            query = "SELECT * FROM concerts WHERE user = ?, date = ?"
            self.c.execute(query, (user, date))

            result = self.c.fetchone()

        # ------------------------------------------------ TABLA USUARIOS ----------------------------------------------
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