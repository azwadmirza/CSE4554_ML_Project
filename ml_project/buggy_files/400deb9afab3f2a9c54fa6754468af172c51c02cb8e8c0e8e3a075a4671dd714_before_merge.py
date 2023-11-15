    def get_feature_meta(column, preprocessing_parameters, backend):
        idx2str, str2idx, str2freq, _, _, _, _ = create_vocabulary(
            column, 'stripped',
            num_most_frequent=preprocessing_parameters['most_common'],
            lowercase=preprocessing_parameters['lowercase'],
            add_padding=False,
            processor=backend.df_engine
        )
        return {
            'idx2str': idx2str,
            'str2idx': str2idx,
            'str2freq': str2freq,
            'vocab_size': len(str2idx)
        }