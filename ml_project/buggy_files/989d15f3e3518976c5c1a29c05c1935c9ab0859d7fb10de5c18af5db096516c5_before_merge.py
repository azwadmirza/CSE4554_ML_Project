    def load_dict(self, file_handle, encoding='utf8'):
        vocab_size, nwords, _ = self.struct_unpack(file_handle, '@3i')
        # Vocab stored by [Dictionary::save](https://github.com/facebookresearch/fastText/blob/master/src/dictionary.cc)
        assert len(self.wv.vocab) == nwords, 'mismatch between vocab sizes'
        assert len(self.wv.vocab) == vocab_size, 'mismatch between vocab sizes'
        self.struct_unpack(file_handle, '@1q')  # number of tokens
        if self.new_format:
            pruneidx_size, = self.struct_unpack(file_handle, '@q')
        for i in range(nwords):
            word_bytes = b''
            char_byte = file_handle.read(1)
            # Read vocab word
            while char_byte != b'\x00':
                word_bytes += char_byte
                char_byte = file_handle.read(1)
            word = word_bytes.decode(encoding)
            count, _ = self.struct_unpack(file_handle, '@qb')
            assert self.wv.vocab[word].index == i, 'mismatch between gensim word index and fastText word index'
            self.wv.vocab[word].count = count

        if self.new_format:
            for j in range(pruneidx_size):
                self.struct_unpack(file_handle, '@2i')