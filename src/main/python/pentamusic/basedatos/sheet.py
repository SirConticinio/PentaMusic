class Sheet:
    def __init__(self, sheet_id, title, owner, is_public, instrument, composer, file_nonce, bars):
        self.title = title
        self.is_public = is_public
        self.sheet_id = sheet_id
        self.owner = owner
        self.composer = composer
        self.instrument = instrument
        self.file_nonce = file_nonce
        self.bars = bars

    def is_encrypted(self):
        return self.is_public == 0
