def _load_fasttext_format(model_file, encoding='utf-8', full_model=True):
    """Load the input-hidden weight matrix from Facebook's native fasttext `.bin` and `.vec` output files.

    Parameters
    ----------
    model_file : str
        Path to the FastText output files.
        FastText outputs two model files - `/path/to/model.vec` and `/path/to/model.bin`
        Expected value for this example: `/path/to/model` or `/path/to/model.bin`,
        as Gensim requires only `.bin` file to the load entire fastText model.
    encoding : str, optional
        Specifies the file encoding.
    full_model : boolean, optional
        If False, skips loading the hidden output matrix. This saves a fair bit
        of CPU time and RAM, but prevents training continuation.

    Returns
    -------
    :class: `~gensim.models.fasttext.FastText`
        The loaded model.

    """
    if not model_file.endswith('.bin'):
        model_file += '.bin'
    with smart_open(model_file, 'rb') as fin:
        m = gensim.models._fasttext_bin.load(fin, encoding=encoding, full_model=full_model)

    model = FastText(
        size=m.dim,
        window=m.ws,
        iter=m.epoch,
        negative=m.neg,
        hs=(m.loss == 1),
        sg=(m.model == 2),
        bucket=m.bucket,
        min_count=m.min_count,
        sample=m.t,
        min_n=m.minn,
        max_n=m.maxn,
    )

    model.vocabulary.raw_vocab = m.raw_vocab
    model.vocabulary.nwords = m.nwords
    model.vocabulary.vocab_size = m.vocab_size
    model.vocabulary.prepare_vocab(model.hs, model.negative, model.wv,
                                   update=True, min_count=model.min_count)

    model.num_original_vectors = m.vectors_ngrams.shape[0]

    model.wv.init_post_load(m.vectors_ngrams)
    model.trainables.init_post_load(model, m.hidden_output)

    _check_model(model)

    logger.info("loaded %s weight matrix for fastText model from %s", m.vectors_ngrams.shape, fin.name)
    return model