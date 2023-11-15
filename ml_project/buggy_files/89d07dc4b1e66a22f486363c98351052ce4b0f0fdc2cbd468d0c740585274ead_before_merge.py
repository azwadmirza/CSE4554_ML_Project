    def get_feature_meta(column, preprocessing_parameters, backend):
        tf_meta = TextFeatureMixin.feature_meta(
            column, preprocessing_parameters, backend
        )
        (
            char_idx2str,
            char_str2idx,
            char_str2freq,
            char_max_len,
            char_pad_idx,
            char_pad_symbol,
            char_unk_symbol,
            word_idx2str,
            word_str2idx,
            word_str2freq,
            word_max_len,
            word_pad_idx,
            word_pad_symbol,
            word_unk_symbol,
        ) = tf_meta
        char_max_len = min(
            preprocessing_parameters['char_sequence_length_limit'],
            char_max_len
        )
        word_max_len = min(
            preprocessing_parameters['word_sequence_length_limit'],
            word_max_len
        )
        return {
            'char_idx2str': char_idx2str,
            'char_str2idx': char_str2idx,
            'char_str2freq': char_str2freq,
            'char_vocab_size': len(char_idx2str),
            'char_max_sequence_length': char_max_len,
            'char_pad_idx': char_pad_idx,
            'char_pad_symbol': char_pad_symbol,
            'char_unk_symbol': char_unk_symbol,
            'word_idx2str': word_idx2str,
            'word_str2idx': word_str2idx,
            'word_str2freq': word_str2freq,
            'word_vocab_size': len(word_idx2str),
            'word_max_sequence_length': word_max_len,
            'word_pad_idx': word_pad_idx,
            'word_pad_symbol': word_pad_symbol,
            'word_unk_symbol': word_unk_symbol,
        }