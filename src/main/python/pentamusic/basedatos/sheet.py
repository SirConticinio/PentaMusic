class Sheet:
    def __init__(self, sheet_id, owner, composer, instrument, title, is_public):
        self.title = title
        self.is_public = is_public
        self.sheet_id = sheet_id
        self.author = owner
        self.composer = composer
        self.instrument = instrument
