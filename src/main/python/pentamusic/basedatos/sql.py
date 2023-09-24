import sqlite3


class SQL:
    def __init__(self):
        # Creamos base de datos
        self.con = sqlite3.connect('penta.db')

        # Esto lo usaremos para poder ejecutar comandos SQL
        self.c = self.con.cursor()

        try:
            # Procedemos a ejecutar un comando en SQL para crear la tabla si no existe
            self.c.execute("""CREATE TABLE IF NOT EXISTS prueba (uno TEXT, dos INTEGER, tres REAL)""")
        except sqlite3.Error as e:
            pass  # No hace nada, si ya existe la tabla

    def insertar(self):
        # Ahora insertamos elementos
        self.c.execute("INSERT INTO prueba VALUES ('hola', 2, 1.9)")

    def consultar(self):
        # Vemos la tabla
        self.c.execute("SELECT * FROM prueba")
        rows = self.c.fetchall()
        for row in rows:
            print(row)

    def cerrar(self):
        # Guardamos los cambios hechos
        self.con.commit()

        # Cerramos la conexión a la base de datos. Buena práctica
        self.con.close()
