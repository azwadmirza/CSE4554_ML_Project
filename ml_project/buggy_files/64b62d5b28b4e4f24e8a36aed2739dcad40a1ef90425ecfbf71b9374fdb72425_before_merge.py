    def load_fasttext_format(cls, model_file, encoding='utf8'):
        """
        Load the input-hidden weight matrix from the fast text output files.

        Note that due to limitations in the FastText API, you cannot continue training
        with a model loaded this way, though you can query for word similarity etc.

        `model_file` is the path to the FastText output files.
        FastText outputs two training files - `/path/to/train.vec` and `/path/to/train.bin`
        Expected value for this example: `/path/to/train`

        """
        model = cls()
        model.wv = cls.load_word2vec_format('%s.vec' % model_file, encoding=encoding)
        model.load_binary_data('%s.bin' % model_file, encoding=encoding)
        return model