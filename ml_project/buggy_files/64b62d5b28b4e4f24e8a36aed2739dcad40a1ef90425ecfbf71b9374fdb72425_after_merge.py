    def load_fasttext_format(cls, model_file, encoding='utf8'):
        """
        Load the input-hidden weight matrix from the fast text output files.

        Note that due to limitations in the FastText API, you cannot continue training
        with a model loaded this way, though you can query for word similarity etc.

        `model_file` is the path to the FastText output files.
        FastText outputs two model files - `/path/to/model.vec` and `/path/to/model.bin`

        Expected value for this example: `/path/to/model` or `/path/to/model.bin`,
        as gensim requires only `.bin` file to load entire fastText model.

        """
        model = cls()
        if not model_file.endswith('.bin'):
            model_file += '.bin'
        model.file_name = model_file
        model.load_binary_data(encoding=encoding)
        return model