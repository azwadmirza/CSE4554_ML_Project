    def convert_token_dict(token_dict):
        """ Convert the dictionary format input token to the CoNLL-U format output token. This is the reverse function of
        `convert_conll_token`.
        Input: dictionary format token, which is a dictionaries for the token.
        Output: CoNLL-U format token, which is a list for the token.
        """
        token_conll = ['_' for i in range(FIELD_NUM)]
        for key in token_dict:
            if key == ID:
                token_conll[FIELD_TO_IDX[key]] = '-'.join([str(x) for x in token_dict[key]]) if isinstance(token_dict[key], tuple) else str(token_dict[key])
            elif key in FIELD_TO_IDX:
                token_conll[FIELD_TO_IDX[key]] = str(token_dict[key])
        # when a word (not mwt token) without head is found, we insert dummy head as required by the UD eval script
        if '-' not in token_conll[FIELD_TO_IDX[ID]] and HEAD not in token_dict:
            token_conll[FIELD_TO_IDX[HEAD]] = str((token_dict[ID] if isinstance(token_dict[ID], int) else token_dict[ID][0]) - 1) # evaluation script requires head: int
        return token_conll