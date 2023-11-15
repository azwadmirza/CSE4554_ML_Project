    def load_dict(self, file_handle, encoding='utf8'):
        vocab_size, nwords, _ = self.struct_unpack(file_handle, '@3i')
        # Vocab stored by [Dictionary::save](https://github.com/facebookresearch/fastText/blob/master/src/dictionary.cc)
        logger.info("loading %s words for fastText model from %s", vocab_size, self.file_name)

        self.struct_unpack(file_handle, '@1q')  # number of tokens
        if self.new_format:
            pruneidx_size, = self.struct_unpack(file_handle, '@q')
        for i in range(vocab_size):
            word_bytes = b''
            char_byte = file_handle.read(1)
            # Read vocab word
            while char_byte != b'\x00':
                word_bytes += char_byte
                char_byte = file_handle.read(1)
            word = word_bytes.decode(encoding)
            count, _ = self.struct_unpack(file_handle, '@qb')

            if i == nwords and i < vocab_size:
                # To handle the error in pretrained vector wiki.fr (French).
                # For more info : https://github.com/facebookresearch/fastText/issues/218

                assert word == "__label__", (
                    'mismatched vocab_size ({}) and nwords ({}), extra word "{}"'.format(vocab_size, nwords, word))
                continue   # don't add word to vocab

            self.wv.vocab[word] = Vocab(index=i, count=count)
            self.wv.index2word.append(word)

        assert len(self.wv.vocab) == nwords, (
            'mismatch between final vocab size ({} words), '
            'and expected number of words ({} words)'.format(len(self.wv.vocab), nwords))
        if len(self.wv.vocab) != vocab_size:
            # expecting to log this warning only for pretrained french vector, wiki.fr
            logger.warning(
                "mismatch between final vocab size (%s words), and expected vocab size (%s words)",
                len(self.wv.vocab), vocab_size)

        if self.new_format:
            for j in range(pruneidx_size):
                self.struct_unpack(file_handle, '@2i')