def compute_bleu(reference_corpus_list, translation_corpus, tokenized=True,
                 tokenizer='13a', max_n=4, smooth=False, lower_case=False,
                 bpe=False, split_compound_word=False):
    r"""Compute bleu score of translation against references.

    Parameters
    ----------
    reference_corpus_list: list of list(list(str)) or list of list(str)
        list of list(list(str)): tokenzied references
        list of list(str): plain text
        List of references for each translation.
    translation_corpus: list(list(str)) or list(str)
        list(list(str)): tokenzied translation
        list(str): plain text
        Translations to score.
    tokenized: bool, default True
        Whether the inputs has been tokenized.
    tokenizer: str or None, default '13a'
        '13a': follow the tokenizer in mteval-v13a.pl
        'intl': follow the international tokenzier in mteval-v14.pl
        None: identity mapping on the string.
        This option is ignored if tokenized is True
    max_n: int, default 4
        Maximum n-gram order to use when computing BLEU score.
    smooth: bool, default False
        Whether or not to compute smoothed bleu score.
    lower_case: bool, default False
        Whether or not to use lower case of tokens
    split_compound_word: bool, default False
        Whether or not to split compound words
        "rich-text format" --> rich ##AT##-##AT## text format.
    bpe: bool, default False
        Whether or not the inputs are in BPE format

    Returns
    -------
    5-Tuple with the BLEU score, n-gram precisions, brevity penalty,
        reference length, and translation length
    """
    precision_numerators = [0 for _ in range(max_n)]
    precision_denominators = [0 for _ in range(max_n)]
    ref_length, trans_length = 0, 0
    for references in reference_corpus_list:
        assert len(references) == len(translation_corpus), \
            'The number of translations and their references do not match'
    if tokenized:
        assert isinstance(reference_corpus_list[0][0], LIST_TYPES) and \
               isinstance(translation_corpus[0], LIST_TYPES), \
            'references and translation should have format of list of list(list(str)) ' \
            'and list(list(str)), respectively, when toknized is True.'
    else:
        assert isinstance(reference_corpus_list[0][0], six.string_types) and \
               isinstance(translation_corpus[0], six.string_types), \
            'references and translation should have format of list(list(str)) ' \
            'and list(str), respectively, when toknized is False.'
    for references, translation in zip(zip(*reference_corpus_list), translation_corpus):
        if not tokenized:
            references = [TOKENIZERS[tokenizer](reference).split() for reference in references]
            translation = TOKENIZERS[tokenizer](translation).split()
        if bpe:
            references = [_bpe_to_words(reference) for reference in references]
            translation = _bpe_to_words(translation)
        if split_compound_word:
            references = [_split_compound_word(reference) for reference in references]
            translation = _split_compound_word(translation)
        if lower_case:
            references = [[w.lower() for w in reference] for reference in references]
            translation = [w.lower() for w in translation]
        trans_len = len(translation)
        trans_length += trans_len
        ref_length += _closest_ref_length(references, trans_len)
        for n in range(max_n):
            matches, candidates = _compute_precision(references, translation, n + 1)
            precision_numerators[n] += matches
            precision_denominators[n] += candidates

    precision_fractions = [(precision_numerators[n], precision_denominators[n])
                           for n in range(max_n)]
    smooth_const = 0
    if smooth:
        smooth_const = 1
    precisions = _smoothing(precision_fractions, smooth_const)
    if min(precisions) > 0:
        precision_log_average = sum(math.log(p) for p in precisions) / max_n
        precision_exp_log_average = math.exp(precision_log_average)
    else:
        precision_exp_log_average = 0

    bp = _brevity_penalty(ref_length, trans_length)
    bleu = precision_exp_log_average*bp

    return bleu, precisions, bp, ref_length, trans_length