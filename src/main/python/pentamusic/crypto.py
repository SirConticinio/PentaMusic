import base64
import os

from PyQt5.QtWidgets import QDialog
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from pentamusic.basedatos.session import Session
from pentamusic.basedatos.sql import SQL
from pentamusic.menus.dialog import Dialog


class Crypto:
    class __Crypto:

        def register_user(self, user_id: str, user_pwd: str):
            salt = os.urandom(16)
            kdf = Scrypt(salt=salt, length=32, n=2 ** 14, r=8, p=1)
            encoded = user_pwd.encode('UTF-8')
            token = kdf.derive(encoded)

            try:
                SQL().insertar_usuario(user_id, token, salt)
                Session.set_session(user_id, token, "")
            except Exception as e:
                Dialog(str(e))

        def login_user(self, user_id, user_pwd) -> bool:
            try:
                salt = SQL().consultar_dato_usuario(user_id, 2)
                token = SQL().consultar_dato_usuario(user_id, 1)
                encoded = user_pwd.encode('UTF-8')
                kdf = Scrypt(salt=salt, length=32, n=2 ** 14, r=8, p=1)

                try:
                    kdf.verify(encoded, token)
                    Session.set_session(user_id, token, "")
                    return True
                except Exception as e:
                    Dialog("La contraseña es incorrecta.")
                    return False

            except Exception as e:
                Dialog(str(e))

        def login_debug(self, debug_username, debug_password):
            if not SQL().consultar_registro(debug_username):
                # tenemos que meter al usuario en la tabla
                salt = os.urandom(16)
                kdf = Scrypt(salt=salt, length=32, n=2 ** 14, r=8, p=1)
                encoded = debug_password.encode('UTF-8')
                token = kdf.derive(encoded)
                SQL().insertar_usuario(debug_username, token, salt)

            # ahora logueamos al usuario
            token = SQL().consultar_dato_usuario(debug_username, 1)
            Session.set_session(debug_username, token, "")

    # Usamos un singleton
    instance = None

    def __new__(cls):
        if not Crypto.instance:
            Crypto.instance = Crypto.__Crypto()
        return Crypto.instance

    def __getattr__(self, item):
        return getattr(self.instance, item)

    def __setattr__(self, key, value):
        return setattr(self.instance, key, value)