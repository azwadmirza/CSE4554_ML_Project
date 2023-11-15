    def load_vectors(self, file_handle):
        if self.new_format:
            self.struct_unpack(file_handle, '@?')  # bool quant_input in fasttext.cc
        num_vectors, dim = self.struct_unpack(file_handle, '@2q')
        # Vectors stored by [Matrix::save](https://github.com/facebookresearch/fastText/blob/master/src/matrix.cc)
        assert self.vector_size == dim, (
            'mismatch between vector size in model params ({}) and model vectors ({})'.format(self.vector_size, dim))
        float_size = struct.calcsize('@f')
        if float_size == 4:
            dtype = np.dtype(np.float32)
        elif float_size == 8:
            dtype = np.dtype(np.float64)

        self.num_original_vectors = num_vectors
        self.wv.syn0_all = np.fromfile(file_handle, dtype=dtype, count=num_vectors * dim)
        self.wv.syn0_all = self.wv.syn0_all.reshape((num_vectors, dim))
        assert self.wv.syn0_all.shape == (self.bucket + len(self.wv.vocab), self.vector_size), \
            'mismatch between actual weight matrix shape {} and expected shape {}'.format(
                self.wv.syn0_all.shape, (self.bucket + len(self.wv.vocab), self.vector_size))

        self.init_ngrams()