def _get_combined_keywords(_keywords, split_text):
    """
    :param keywords:dict of keywords:scores
    :param split_text: list of strings
    :return: combined_keywords:list
    """
    result = []
    _keywords = _keywords.copy()
    len_text = len(split_text)
    for i in xrange(len_text):
        word = _strip_word(split_text[i])
        if word in _keywords:
            combined_word = [word]
            if i + 1 == len_text:
                result.append(word)   # appends last word if keyword and doesn't iterate
            for j in xrange(i + 1, len_text):
                other_word = _strip_word(split_text[j])
                if other_word in _keywords and other_word == split_text[j] and not other_word in combined_word:
                    combined_word.append(other_word)
                else:
                    for keyword in combined_word:
                        _keywords.pop(keyword)
                    result.append(" ".join(combined_word))
                    break
    return result