class Sheet:
    def __init__(self, sheet_id, title, owner, is_public, instrument, composer):
        self.title = title
        self.is_public = is_public
        self.sheet_id = sheet_id
        self.owner = owner
        self.composer = composer
        self.instrument = instrument
