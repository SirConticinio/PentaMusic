import sqlite3

class SQL:
    class __SQL:
        def __init__(self):
            # Creamos base de datos
            self.con = sqlite3.connect('penta.db')

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
                                id NUMERIC PRIMARY KEY,
                                nombre_creador TEXT,
                                nombre_partitura TEXT NOT NULL,
                                publica NUMERIC,
                                CONSTRAINT CK_Partitura_publico CHECK (publica IN (0, 1))
            )""")
            self.c.execute("""CREATE TABLE IF NOT EXISTS user_partituras (
                                                user TEXT,
                                                partitura NUMERIC,
                                                comentarios TEXT,
                                                compas TEXT,
                                                PRIMARY KEY (user, partitura),
                                                FOREIGN KEY (user) REFERENCES usuarios(user),
                                                FOREIGN KEY (partitura) REFERENCES partitura(id)
                            )""")
            self.c.execute("""CREATE TRIGGER IF NOT EXISTS insert_user_partitura
                                AFTER INSERT ON partitura
                                FOR EACH ROW
                                BEGIN
                                    insert into user_partitura values (NEW.nombre_creador, NEW.id);
                                END;""")

            self.c.execute("""CREATE TRIGGER IF NOT EXISTS insertar_user_partitura 
                                BEFORE INSERT ON user_partituras
                                FOR EACH ROW
                                BEGIN
                                    -- Consulta para verificar si el usuario puede realizar la inserción
                                    SELECT RAISE(ABORT, 'No tienes permiso para insertar en user_partitura')
                                    WHERE NEW.user != NEW.nombre_creador AND NEW.publico != 1;
                                END;""")

            self.c.execute("""CREATE VIEW IF NOT EXISTS hola AS SELECT * FROM partitura WHERE publica = 1""")


        def insertar(self, user: str, password: str) -> None:
            # Ahora insertamos elementos
            if not self.consultar(user, password):
                query = "INSERT INTO usuarios (user, password) VALUES (?, ?)"
                # Tupla con los valores a insertar
                values = (user, password)
                self.c.execute(query, values)
                self.con.commit()
            else:
                print("El usuario ya existe")

        def consultar(self, user: str, password: str) -> bool:
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
        return getattr(self.instance,item)

    def __setattr__(self, key, value):
        return setattr(self.instance,key,value)

if __name__ == "__main__":
    print("Hola")

