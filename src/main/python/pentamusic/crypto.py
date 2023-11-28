import base64
import os
import shutil
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import QDialog
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat._oid import NameOID
from cryptography.hazmat.primitives import cmac, hashes, hmac, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from pentamusic.basedatos.session import Session
from pentamusic.menus.dialog import OkDialog
from dotenv import load_dotenv


class Crypto:
    class __Crypto:
        loaded_env = False
        basepath = os.path.expanduser("~/PentaMusic")

        def register_user(self, user_id: str, user_pwd: str) -> bool:
            salt = os.urandom(16)
            salt_for_encryption = os.urandom(16)
            kdf = Scrypt(salt=salt, length=32, n=2 ** 14, r=8, p=1)
            encoded = user_pwd.encode('UTF-8')
            token = kdf.derive(encoded)

            try:
                from pentamusic.basedatos.sql import SQL
                SQL().insert_user(user_id, token, salt, salt_for_encryption)
                self.set_session(user_id, user_pwd, salt_for_encryption)

                # Por último, guardamos el usuario
                try:
                    self.sign_user(user_id)
                    OkDialog("¡Bienvenido a PentaMusic!\nSe ha generado un recibo en la carpeta del programa"
                             "\ncon tus datos de registro.")
                except Exception as e:
                    OkDialog("Se ha producido un error durante el firmado de datos de usuario.\n" + str(e))
                    return False
            except Exception as e:
                OkDialog("Ha ocurrido un error durante el proceso de registro:\n" + str(e))
                return False

            # Si llegamos hasta aquí, el registro ha terminado con éxito
            return True

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

        def get_sign_password(self, key) -> bytes:
            # Cargamos la contraseña del entorno si no lo hemos hecho antes
            if not self.loaded_env:
                load_dotenv(self.basepath + "/OpenSSL/private.env")
                self.loaded_env = True

            value = os.getenv(key)
            if value is None or value.strip() == "":
                raise Exception("¡No se han configurado las contraseñas del entorno!"
                                "\nNo se pueden realizar operaciones con certificados.")
            return value.encode('UTF-8')

        def get_sign_private_key(self) -> RSAPrivateKey:
            # Buscamos a ver si la clave ya existe, si no la generamos
            path = self.basepath + "/OpenSSL/APP/private_key.pem"
            if os.path.exists(path):
                # Lo leemos del archivo
                with open(path, "rb") as key_file:
                    return serialization.load_pem_private_key(
                        key_file.read(),
                        password=self.get_sign_password("PENTAMUSIC_PWD"),
                    )
            else:
                # Generamos la contraseña y la serializamos
                private = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )
                pem = private.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.BestAvailableEncryption(self.get_sign_password("PENTAMUSIC_PWD")),
                )
                with open(path, "wb") as key_file:
                    key_file.write(pem)

                # Una vez generada y guardada la clave privada, vamos a certificarla
                self.generate_certificate()
                return private

        def sign_user(self, user: str):
            # Vamos a firmar un recibo de registro de usuario
            day = datetime.now().strftime("%d/%m/%Y")
            hour = datetime.now().strftime("%H:%M:%S")
            datos = f"El usuario: '{user}', se ha registrado a día '{day}' y hora '{hour}'."
            signature = self.get_sign_private_key().sign(
                datos.encode('UTF-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            # Creamos el recibo
            date = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            emisor = "PentaMusic - UC3M"
            base = base64.b64encode(signature).decode('ASCII')
            recibo = f"===== RECIBO DIGITAL =====\nEmisor: {emisor}\nFecha: {date}\n\nMensaje:\n{datos}\n\nFirma:\n{base}\n==========================\n"

            # Y lo guardamos en fichero
            tickets = self.basepath + "/Tickets"
            path = tickets + "/" + user + ".pem"
            if not os.path.exists(tickets):
                os.mkdir(tickets)
            if os.path.exists(path):
                os.remove(path)
            with open(path, "w") as file:
                file.write(recibo)
            print(f"\n\nSe ha firmado el usuario con el siguiente recibo:\n{recibo}")

        def get_ticket_data(self, filepath: str, header: str, is_base64: bool) -> bytes:
            with open(filepath, "r") as file:
                lines = file.readlines()
                index = 0
                for line in lines:
                    if line.strip() == header:
                        data = lines[index+1].strip()
                        return base64.b64decode(data) if is_base64 else data.encode('UTF-8')
                    index += 1
            return b""

        def verify_user(self, user: str):
            # Leemos el archivo que contiene el recibo del usuario
            path = self.basepath + "/Tickets/" + user + ".pem"
            message = self.get_ticket_data(path, "Mensaje:", False)
            data = self.get_ticket_data(path, "Firma:", True)

            # Y ahora probamos con la public key
            try:
                public_key = self.get_sign_public_key()
                try:
                    public_key.verify(
                        data,
                        message,
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH
                        ),
                        hashes.SHA256()
                    )
                    OkDialog("¡Se ha verificado el usuario correctamente!\n" + message.decode('UTF-8'))
                except InvalidSignature as e:
                    OkDialog("¡La firma no ha podido ser verificada!\n" + str(e))
            except Exception as e:
                OkDialog(str(e))

        def get_sign_public_key(self) -> RSAPublicKey:
            # Lee la clave pública ya certificada y la devuelve
            path = self.basepath + f"/OpenSSL/APP/CERT_PENTAMUSIC.pem"
            if not os.path.exists(path):
                raise Exception("¡No se ha generado el certificado de clave pública de la aplicación!")

            with open(path, "rb") as key_file:
                cert = x509.load_pem_x509_certificate(key_file.read())

                # Leemos el certificado y verificamos que siga siendo correcto
                path = self.basepath + "/OpenSSL/APP/"
                origin = self.basepath + "/OpenSSL/AC1/ac1cert.pem"
                verify = self.basepath + "/OpenSSL/APP/CERT_PENTAMUSIC.pem"
                result_key = os.popen(f"cd {path} && openssl verify -CAfile {origin} {verify}").read()
                result_ac1 = os.popen(f"cd {path} && openssl verify -CAfile {origin} {origin}").read()
                if result_key.strip() == f"{verify}: OK" and result_ac1.strip() == f"{origin}: OK":
                    print("¡Se ha verificado que la clave pública es válida!")
                    return cert.public_key()
                else:
                    raise Exception("¡La clave pública generada no es válida!")

        def generate_openssl_system(self):
            # Generamos todas las carpetas necesarias
            path = self.basepath + "/OpenSSL/"
            ac1 = path + "AC1/"
            if not os.path.exists(path):
                # Generamos los sistemas de carpetas
                os.mkdir(path)
                os.mkdir(path + "APP")
                os.mkdir(path + "AC1")
                os.mkdir(path + "AC1/solicitudes")
                os.mkdir(path + "AC1/crls")
                os.mkdir(path + "AC1/nuevoscerts")
                os.mkdir(path + "AC1/privado")

                # Copiamos todos los archivos de configuración
                configpath = Path(__file__).absolute().parent.as_posix() + "/certconfig/"
                shutil.copy2(configpath + "index.txt", ac1)
                shutil.copy2(configpath + "serial", ac1)
                shutil.copy2(configpath + "openssl_AC1.cnf", ac1)
                shutil.copy2(configpath + "private.env", path)

            cert = ac1 + "ac1cert.pem"
            if not os.path.exists(cert):
                # Generamos el sistema de AC1
                pwd = self.get_sign_password("AC1_PWD")
                config = ac1 + "openssl_AC1.cnf"
                print("¡Generando el certificado de AC1!")
                os.system(f"cd {ac1} && openssl req -x509 -newkey rsa:2048 -days 360 -out {cert} -outform PEM -config {config} -passout pass:\"{pwd}\"")
                print("\nLos datos del certificado son los siguientes:")
                os.system(f"cd {ac1} && openssl x509 -in {cert} -text -noout")

        def create_certificate_request(self):
            # Generamos la solicitud de certificado desde el código con nuestros datos
            csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "MADRID"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "UC3M"),
                x509.NameAttribute(NameOID.COMMON_NAME, "PENTAMUSIC"),
            ])).sign(self.get_sign_private_key(), hashes.SHA256())

            # La guardamos en nuestra carpeta para pasársela a AC1
            path = self.basepath + f"/OpenSSL/APP/CSR_PENTAMUSIC.pem"
            with open(path, "wb") as f:
                f.write(csr.public_bytes(serialization.Encoding.PEM))
            # La copiamos a AC1
            shutil.copy2(path, self.basepath + "/OpenSSL/AC1/solicitudes")

        def generate_certificate(self):
            # Generamos la solicitud de certificado
            self.create_certificate_request()

            # La procesamos desde AC1 para que la certifique
            path = self.basepath + "/OpenSSL/AC1/"
            request = path + "solicitudes/CSR_PENTAMUSIC.pem"
            config = path + "openssl_AC1.cnf"
            out = path + "nuevoscerts/01.pem"
            pwd = self.get_sign_password("AC1_PWD")
            print("¡Generamos el certificado del sistema!")
            os.system(f"cd {path} && openssl ca -batch -in {request} -notext -config {config} -passin pass:\"{pwd}\"")
            print("\nLos datos del certificado son los siguientes:")
            os.system(f"cd {path} && openssl x509 -in {out} -text -noout")


            # Finalmente se la devolvemos a la carpeta de APP
            final = self.basepath + "/OpenSSL/APP/CERT_PENTAMUSIC.pem"
            os.system(f"cp {out} {final}")

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