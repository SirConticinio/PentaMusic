import base64
import os

from PyQt5.QtWidgets import QDialog
from cryptography.hazmat.primitives import cmac, hashes, hmac
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from pentamusic.basedatos.session import Session
from pentamusic.menus.dialog import OkDialog


class Crypto:
    class __Crypto:
        def register_user(self, user_id: str, user_pwd: str):
            salt = os.urandom(16)
            salt_for_encryption = os.urandom(16)
            kdf = Scrypt(salt=salt, length=32, n=2 ** 14, r=8, p=1)
            encoded = user_pwd.encode('UTF-8')
            token = kdf.derive(encoded)

            try:
                from pentamusic.basedatos.sql import SQL
                SQL().insert_user(user_id, token, salt, salt_for_encryption)
                self.set_session(user_id, user_pwd, salt_for_encryption)
            except Exception as e:
                OkDialog("Ha ocurrido un error durante el proceso de registro:\n" + str(e))

        def set_session(self, user_id: str, user_pwd: str, salt_for_encryption):
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt_for_encryption,
                iterations=480000,
            )
            key = kdf.derive(user_pwd.encode('UTF-8'))
            # Ahora que tenemos la clave de cifrado del usuario, la guardamos en la sesión
            Session.set_session(user_id, key)
            # Si hemos iniciado sesión correctamente, rotamos la clave + salt para que no sea siempre el mismo
            self.rotate_token(user_id, user_pwd, salt_for_encryption)

        def login_user(self, user_id, user_pwd) -> bool:
            try:
                from pentamusic.basedatos.sql import SQL
                salt = SQL().get_user_data(user_id, 2)
                token = SQL().get_user_data(user_id, 1)
                salt_for_encryption = SQL().get_user_data(user_id, 3)
                encoded = user_pwd.encode('UTF-8')
                # Usamos Scrypt para comprobar si el token de la clave guardado coincide con el de la clave introducida
                kdf = Scrypt(salt=salt, length=32, n=2 ** 14, r=8, p=1)

                try:
                    kdf.verify(encoded, token)
                    self.set_session(user_id, user_pwd, salt_for_encryption)
                    # Aquí hemos iniciado sesión correctamente
                    return True
                except Exception as e:
                    OkDialog("La contraseña es incorrecta.")
                    return False
            except Exception as e:
                OkDialog("Ha ocurrido un error durante el proceso de inicio de sesión:\n" + str(e))

        def rotate_token(self, user_id, user_pwd, salt_for_encryption):
            salt = os.urandom(16)
            kdf = Scrypt(salt=salt, length=32, n=2 ** 14, r=8, p=1)
            encoded = user_pwd.encode('UTF-8')
            token = kdf.derive(encoded)

            try:
                from pentamusic.basedatos.sql import SQL
                SQL().update_user(user_id, token, salt, salt_for_encryption)
            except Exception as e:
                OkDialog("Ha ocurrido un error rotando las claves:\n" + str(e))

        def encrypt_data(self, decrypted_data, nonce) -> bytes:
            try:
                chacha = ChaCha20Poly1305(Session().key)
                data = bytes(decrypted_data, 'utf-8') if type(decrypted_data) == str else bytes(decrypted_data)
                return chacha.encrypt(nonce, data, None)
            except Exception as e:
                OkDialog("Ha ocurrido un error encriptando los datos:\n" + str(e))

        def decrypt_data(self, encrypted_data, nonce, should_decode=True) -> str:
            try:
                chacha = ChaCha20Poly1305(Session().key)
                decrypted = chacha.decrypt(nonce, encrypted_data, None)
                if should_decode:
                    decrypted = decrypted.decode('utf-8')
                return decrypted
            except Exception as e:
                OkDialog("Ha ocurrido un error desencriptando los datos:\n" + str(e))

        # Debug utilizado durante el desarrollo de la aplicación, que no pertenece al producto final:
        """
        def login_debug(self, debug_username, debug_password):
            from pentamusic.basedatos.sql import SQL
            if not SQL().get_registration(debug_username):
                # tenemos que meter al usuario en la tabla
                salt = os.urandom(16)
                salt_for_encryption = os.urandom(16)
                kdf = Scrypt(salt=salt, length=32, n=2 ** 14, r=8, p=1)
                encoded = debug_password.encode('UTF-8')
                token = kdf.derive(encoded)
                SQL().insert_user(debug_username, token, salt, salt_for_encryption)

            # ahora logueamos al usuario
            self.set_session(debug_username, debug_password, SQL().get_user_data(debug_username, 3))"""


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