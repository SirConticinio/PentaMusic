
class Session():

    class __Session:
        def __init__(self, usuario: str, key: str):
            self.user = usuario
            self.key = key

    # Usamos un singleton
    instance = None

    def __new__(cls):
        return Session.instance

    @staticmethod
    def set_session(usuario, key):
        Session.instance = Session.__Session(usuario, key)
        return Session.instance

    @staticmethod
    def revoke():
        Session.instance.key = b""
        Session.instance = None

    def __getattr__(self, item):
        return getattr(self.instance,item)

    def __setattr__(self, key, value):
        return setattr(self.instance,key,value)
