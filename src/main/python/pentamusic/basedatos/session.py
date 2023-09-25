
class Session():

    class __Session:
        def __init__(self, usuario: str, password: str):
            self.user = usuario
            self.pwd = password

    # Usamos un singleton
    instance = None

    def __new__(cls):
        return Session.instance

    @staticmethod
    def set_session(usuario, password):
        Session.instance = Session.__Session(usuario, password)
        return Session.instance

    def __getattr__(self, item):
        return getattr(self.instance,item)

    def __setattr__(self, key, value):
        return setattr(self.instance,key,value)
