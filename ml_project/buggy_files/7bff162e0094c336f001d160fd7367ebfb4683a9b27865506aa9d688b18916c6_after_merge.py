    def get_feature_meta(column, preprocessing_parameters, backend):
        column = column.astype(str)
        idx2str, str2idx, str2freq, max_length, _, _, _ = create_vocabulary(
            column, preprocessing_parameters['tokenizer'],
            lowercase=preprocessing_parameters['lowercase'],
            num_most_frequent=preprocessing_parameters['most_common'],
            vocab_file=preprocessing_parameters['vocab_file'],
            unknown_symbol=preprocessing_parameters['unknown_symbol'],
            padding_symbol=preprocessing_parameters['padding_symbol'],
            processor=backend.df_engine
        )
        max_length = min(
            preprocessing_parameters['sequence_length_limit'],
            max_length
        )
        return {
            'idx2str': idx2str,
            'str2idx': str2idx,
            'str2freq': str2freq,
            'vocab_size': len(idx2str),
            'max_sequence_length': max_length
        }