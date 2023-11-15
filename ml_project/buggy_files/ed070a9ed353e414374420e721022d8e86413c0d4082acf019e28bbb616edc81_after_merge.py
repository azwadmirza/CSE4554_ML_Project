    def __init__(
        self, word_id_map={}, pad_token_id=None, unk_token_id=None, max_length=256
    ):
        super().__init__(
            word_id_map=word_id_map,
            unk_token_id=unk_token_id,
            pad_token_id=pad_token_id,
            lowercase=True,
        )
        self.pad_id = pad_token_id
        self.oov_id = unk_token_id
        self.convert_id_to_word = self.id_to_token
        # Set defaults.
        self.enable_padding(length=max_length, pad_id=pad_token_id)
        self.enable_truncation(max_length=max_length)