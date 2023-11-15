def tokenize(snippet):
    """Split snippet into well-defined tokens."""
    tokens = []
    word = ''
    i = 0
    last_name = None
    while i < len(snippet):
        c = snippet[i]
        if whitespace.match(c) is not None:
            if last_name is not None:
                token = Token(last_name, word, 1, i + 1)
                tokens.append(token)
            token = Token('whitespace', c, line=1, col=i + 1)
            tokens.append(token)
            word = ''
            last_name = None
            i += 1
        else:
            temp_word = word + c
            match_found = False
            for token_name in token_regex:
                regex = token_regex[token_name]
                if regex.match(temp_word) is not None:
                    last_name = token_name
                    match_found = True
                    word = temp_word
                    break
            if not match_found:
                if last_name is not None:
                    token = Token(last_name, word, 1, i + 1)
                    tokens.append(token)
                    word = ''
                    last_name = None
            else:
                word = temp_word
                i += 1
    if last_name is not None:
        token = Token(last_name, word, 1, i + 1)
        tokens.append(token)
    return tokens