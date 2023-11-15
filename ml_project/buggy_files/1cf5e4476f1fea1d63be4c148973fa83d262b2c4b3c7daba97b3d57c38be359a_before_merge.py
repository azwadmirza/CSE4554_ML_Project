def _load_vocab(fin, new_format, encoding='utf-8'):
    """Load a vocabulary from a FB binary.

    Before the vocab is ready for use, call the prepare_vocab function and pass
    in the relevant parameters from the model.

    Parameters
    ----------
    fin : file
        An open file pointer to the binary.
    new_format: boolean
        True if the binary is of the newer format.
    encoding : str
        The encoding to use when decoding binary data into words.

    Returns
    -------
    tuple
        The loaded vocabulary.  Keys are words, values are counts.
        The vocabulary size.
        The number of words.
    """
    vocab_size, nwords, nlabels = _struct_unpack(fin, '@3i')

    # Vocab stored by [Dictionary::save](https://github.com/facebookresearch/fastText/blob/master/src/dictionary.cc)
    if nlabels > 0:
        raise NotImplementedError("Supervised fastText models are not supported")
    logger.info("loading %s words for fastText model from %s", vocab_size, fin.name)

    _struct_unpack(fin, '@1q')  # number of tokens
    if new_format:
        pruneidx_size, = _struct_unpack(fin, '@q')

    raw_vocab = collections.OrderedDict()
    for i in range(vocab_size):
        word_bytes = b''
        char_byte = fin.read(1)
        # Read vocab word
        while char_byte != b'\x00':
            word_bytes += char_byte
            char_byte = fin.read(1)
        word = word_bytes.decode(encoding)
        count, _ = _struct_unpack(fin, '@qb')
        raw_vocab[word] = count

    if new_format:
        for j in range(pruneidx_size):
            _struct_unpack(fin, '@2i')

    return raw_vocab, vocab_size, nwords