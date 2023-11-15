def _replace_consonants(word: str, consonants: str) -> str:
    _HO_HIP = "\u0e2b"  # ห
    _RO_RUA = "\u0e23"  # ร

    if not consonants:
        return word

    if len(consonants) == 1:
        return word.replace(consonants[0], _CONSONANTS[consonants[0]][0])

    i = 0
    len_cons = len(consonants)
    while i < len_cons:
        if i == 0:
            if consonants[0] == _HO_HIP:
                word = word.replace(consonants[0], "")
                del consonants[0]
                len_cons -= 1
            else:
                word = word.replace(
                    consonants[0], _CONSONANTS[consonants[0]][0]
                )
                i += 1
        elif consonants[i] == _RO_RUA and i == len(word) and word[i - 1] == _RO_RUA:
            word = word.replace(
                    consonants[i], _CONSONANTS[consonants[i]][1]
            )
        elif consonants[i] == _RO_RUA and i < len(word):
            if i + 1 == len(word) and word[i] == _RO_RUA:
                word = word.replace(
                    consonants[i], _CONSONANTS[consonants[i]][1]
                )
            elif word[i] == _RO_RUA and i + 1 < len(word):
                if word[i + 1] == _RO_RUA:
                    word = list(word)
                    del word[i + 1]
                    if i + 2 == len_cons:
                        word[i] = "an"
                    else:
                        word[i] = "a"
                    word = "".join(word)
                    i += 1
                elif word[i] == _RO_RUA:
                    word = word.replace(
                        consonants[i], _CONSONANTS[consonants[i]][1]
                    )
                    i += 1
                else:
                    word = word.replace(
                        consonants[i],
                        _CONSONANTS[consonants[i]][1]
                    )
                    i += 1
            elif word[i] == _RO_RUA:
                word = word.replace(
                    consonants[i], _CONSONANTS[consonants[i]][1]
                )
                i += 1
            else:
                word = word.replace(
                    consonants[i],
                    _CONSONANTS[consonants[i]][1]
                )
                i += 1
        else:
            word = word.replace(consonants[i], _CONSONANTS[consonants[i]][1])
            i += 1

    return word