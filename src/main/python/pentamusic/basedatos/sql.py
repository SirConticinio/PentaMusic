import sqlite3


class SQL:
    def __init__(self):
        # Creamos base de datos
        self.con = sqlite3.connect('penta.db')

        # Esto lo usaremos para poder ejecutar comandos SQL
        self.c = self.con.cursor()

        try:
            # Procedemos a ejecutar un comando en SQL para crear la tabla si no existe
            self.c.execute("""CREATE TABLE IF NOT EXISTS usuarios (USER TEXT, password TEXT)""")
        except sqlite3.Error as e:
            pass  # No hace nada, si ya existe la tabla

    def insertar(self, user: str, password: str) -> None:
        # Ahora insertamos elementos
        query = "INSERT INTO usuarios (user, password) VALUES (?, ?)"
        # Tupla con los valores a insertar
        values = (user, password)
        self.c.execute(query, values)

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
