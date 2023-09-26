import os
import sqlite3

from pentamusic.basedatos.sheet import Sheet

class SQL:
    class __SQL:
        def __init__(self):
            # Creamos base de datos
            file = os.path.expanduser("~/PentaMusic")
            if not os.path.exists(file):
                os.makedirs(file)
            self.con = sqlite3.connect(file + "/penta.db")

            # Esto lo usaremos para poder ejecutar comandos SQL
            self.c = self.con.cursor()

            # Creamos nuestra base de datos
            self.c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
                                USER TEXT PRIMARY KEY, 
                                password TEXT NOT NULL 
            )""")
            self.c.execute("""CREATE TABLE IF NOT EXISTS conciertos (
                                id numeric PRIMARY KEY,
                                user TEXT,
                                nombre_concierto TEXT NOT NULL,
                                fecha DATE,
                                lugar TEXT NOT NULL,
                                FOREIGN KEY (user) REFERENCES usuarios(user)
            )""")
            self.c.execute("""CREATE TABLE IF NOT EXISTS partitura (
                                id TEXT PRIMARY KEY,
                                nombre_partitura TEXT NOT NULL,
                                nombre_creador TEXT NOT NULL,
                                publica NUMERIC,
                                instrumento TEXT, 
                                compositor TEXT,
                                CONSTRAINT CK_Partitura_publico CHECK (publica IN (0, 1))
            )""")
            self.c.execute("""CREATE TABLE IF NOT EXISTS user_partitura (
                                                user TEXT,
                                                partitura NUMERIC,
                                                comentarios TEXT,
                                                compas TEXT,
                                                PRIMARY KEY (user, partitura),
                                                FOREIGN KEY (user) REFERENCES usuarios(user),
                                                FOREIGN KEY (partitura) REFERENCES partitura(id)
                            )""")
            self.c.execute("""CREATE TRIGGER insert_partitura
                                            AFTER INSERT ON partitura
                                            FOR EACH ROW
                                            BEGIN
                                                insert into user_partitura values (NEW.id, NEW.nombre_creador, NULL, NULL);
                                            END;
                            """)

            self.c.execute("""CREATE VIEW IF NOT EXISTS hola AS SELECT * FROM partitura WHERE publica = 1""")

        # -------------------------------------------- TABLA PARTITURAS ------------------------------------------------
        def insertar_partituras(self, id, nombre_partitura, nombre_creador, publica, compositor=None,
                                instrumento=None):
            query = ("INSERT INTO partitura (id, nombre_partitura, nombre_creador, publica, compositor, instrumento) "
                     "VALUES (?, ?, ?, ?, ?, ?)")
            # Tupla con los valores a insertar
            values = (id, nombre_partitura, nombre_creador, publica, compositor, instrumento)
            self.c.execute(query, values)
            self.con.commit()

        def consult_partiture(self, id: str) -> Sheet:
            query = "SELECT * FROM partitura WHERE id = ?"
            self.c.execute(query, (id,))

            result = self.c.fetchone()

            if result is not None:
                print(result[0], result[1], result[2], result[3], result[4], result[5])
                return Sheet(result[0], result[1], result[2], result[3], result[4], result[5])

        # -------------------------------------------- TABLA CONCIERTO -------------------------------------------------
        def insertar_concierto(self, id, nombre_partitura, publica, nombre_creador=None, compositor=None,
                                instrumento=None):
            query = ("INSERT INTO partitura (id, nombre_creador, compositor, instrumento, nombre_partitura, publica) "
                     "VALUES (?, ?, ?, ?, ?, ?)")
            # Tupla con los valores a insertar
            values = (id, nombre_creador, compositor, instrumento, nombre_partitura, publica)
            self.c.execute(query, values)
            self.con.commit()

        def consult_concert(self, id: str) -> Sheet:
            query = "SELECT * FROM partitura WHERE id = ?"
            self.c.execute(query, (id,))

            result = self.c.fetchone()

            if result is not None:
                return Sheet(result[0], result[1], result[2], result[3], result[4], result[5])

        # ------------------------------------------------ TABLA USUARIOS ----------------------------------------------
        def insertar(self, user: str, password: str) -> None:
            # Ahora insertamos elementos
            if not self.consultar_reg(user):
                query = "INSERT INTO usuarios (user, password) VALUES (?, ?)"
                # Tupla con los valores a insertar
                values = (user, password)
                self.c.execute(query, values)
                self.con.commit()
            else:
                print("El usuario ya existe")

        def consultar_reg(self, user):
            query = "SELECT * FROM usuarios WHERE user = ?"
            self.c.execute(query, (user,))

            # Recuperamos los resultados de la consulta
            result = self.c.fetchone()

            # Si result es None, significa que no se encontró en la tabla
            if result is None:
                print("No encontrado")
                return False
            else:
                print("Encontrado")
                return True

        def consulta_log(self, user: str, password: str) -> bool:
            query = "SELECT * FROM usuarios WHERE user = ? AND password = ?"
            values = (user, password)
            self.c.execute(query, values)

            # Recuperamos los resultados de la consulta
            result = self.c.fetchone()

            # Si result es None, significa que no se encontró en la tabla
            if result is None:
                print("No encontrado")
                return False
            else:
                print("Encontrado")
                return True

        # Se usa para cerrar la base de datos
        def cerrar(self):
            # Guardamos los cambios hechos
            self.con.commit()

            # Cerramos la conexión a la base de datos. Buena práctica
            self.con.close()

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


if __name__ == "__main__":
    print("Hola")
