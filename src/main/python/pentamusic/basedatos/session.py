
class Session():

    class __Session:
        def __init__(self, usuario: str, password: str, master_key: str):
            self.user = usuario
            self.pwd = password
            self.key = master_key

    # Usamos un singleton
    instance = None

    def __new__(cls):
        return Session.instance

    @staticmethod
    def set_session(usuario, password, key):
        Session.instance = Session.__Session(usuario, password, key)
        return Session.instance

    @staticmethod
    def revoke():
        Session.instance = None

    def __getattr__(self, item):
        return getattr(self.instance,item)

    def __setattr__(self, key, value):
        return setattr(self.instance,key,value)
