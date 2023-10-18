import base64
import os

from PyQt5.QtWidgets import QDialog
from cryptography.hazmat.primitives import cmac, hashes, hmac
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from pentamusic.basedatos.session import Session
from pentamusic.menus.dialog import OkDialog


class Crypto:
    class __Crypto:

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!! CLAVE MAESTRA !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # !!!            En una aplicación real, no se podria poner aquí             !!!
        # !!!           Sentimos mucho tener que realizar tal sacrilegio             !!!
        # !!!                                                                        !!!
        master_key = b"WlMOV4OAHRZRjdlGAPziM0IrzCCBxChXwQZltSKVBMHnw7MHXBPJR8N6VQ7kIEc4"
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        def register_user(self, user_id: str, user_pwd: str):
            salt = os.urandom(16)
            kdf = Scrypt(salt=salt, length=32, n=2 ** 14, r=8, p=1)
            encoded = user_pwd.encode('UTF-8')
            token = kdf.derive(encoded)

            try:
                from pentamusic.basedatos.sql import SQL
                SQL().insertar_usuario(user_id, token, salt)
                self.set_session(user_id, user_pwd)
            except Exception as e:
                OkDialog(str(e))

        def set_session(self, user_id: str, user_pwd: str):
            h = hmac.HMAC(self.master_key, hashes.SHA256())
            encoded = user_pwd.encode('UTF-8')
            h.update(encoded)
            signature = h.finalize()
            # ahora que tenemos la clave de cifrado del usuario, la guardamos en la sesión
            Session.set_session(user_id, signature)

        def login_user(self, user_id, user_pwd) -> bool:
            try:
                from pentamusic.basedatos.sql import SQL
                salt = SQL().consultar_dato_usuario(user_id, 2)
                token = SQL().consultar_dato_usuario(user_id, 1)
                encoded = user_pwd.encode('UTF-8')
                kdf = Scrypt(salt=salt, length=32, n=2 ** 14, r=8, p=1)

                try:
                    kdf.verify(encoded, token)
                    self.set_session(user_id, user_pwd)
                    return True
                except Exception as e:
                    OkDialog("La contraseña es incorrecta.")
                    return False

            except Exception as e:
                OkDialog(str(e))

        def login_debug(self, debug_username, debug_password):
            from pentamusic.basedatos.sql import SQL
            if not SQL().consultar_registro(debug_username):
                # tenemos que meter al usuario en la tabla
                salt = os.urandom(16)
                kdf = Scrypt(salt=salt, length=32, n=2 ** 14, r=8, p=1)
                encoded = debug_password.encode('UTF-8')
                token = kdf.derive(encoded)
                SQL().insertar_usuario(debug_username, token, salt)

            # ahora logueamos al usuario
            self.set_session(debug_username, debug_password)

        def decrypt_data(self, encrypted_data, nonce) -> str:
            chacha = ChaCha20Poly1305(Session().key)
            return str(chacha.decrypt(nonce, encrypted_data, None))

        def encrypt_data(self, decrypted_data, nonce) -> bytes:
            chacha = ChaCha20Poly1305(Session().key)
            data = bytes(decrypted_data, 'utf-8') if type(decrypted_data) == str else bytes(decrypted_data)
            return chacha.encrypt(nonce, data, None)



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