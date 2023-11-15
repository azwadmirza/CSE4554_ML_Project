def load_old_word2vec(*args, **kwargs):
    old_model = Word2Vec.load(*args, **kwargs)
    params = {
        'size': old_model.vector_size,
        'alpha': old_model.alpha,
        'window': old_model.window,
        'min_count': old_model.min_count,
        'max_vocab_size': old_model.__dict__.get('max_vocab_size', None),
        'sample': old_model.sample,
        'seed': old_model.seed,
        'workers': old_model.workers,
        'min_alpha': old_model.min_alpha,
        'sg': old_model.sg,
        'hs': old_model.hs,
        'negative': old_model.negative,
        'cbow_mean': old_model.cbow_mean,
        'hashfxn': old_model.hashfxn,
        'iter': old_model.iter,
        'null_word': old_model.null_word,
        'sorted_vocab': old_model.sorted_vocab,
        'batch_words': old_model.batch_words,
        'compute_loss': old_model.__dict__.get('compute_loss', None)
    }
    new_model = NewWord2Vec(**params)
    # set trainables attributes
    new_model.wv.vectors = old_model.wv.syn0
    if hasattr(old_model.wv, 'syn0norm'):
        new_model.wv.vectors_norm = old_model.wv.syn0norm
    if hasattr(old_model, 'syn1'):
        new_model.trainables.syn1 = old_model.syn1
    if hasattr(old_model, 'syn1neg'):
        new_model.trainables.syn1neg = old_model.syn1neg
    if hasattr(old_model, 'syn0_lockf'):
        new_model.trainables.vectors_lockf = old_model.syn0_lockf
    # set vocabulary attributes
    new_model.wv.vocab = old_model.wv.vocab
    new_model.wv.index2word = old_model.wv.index2word
    new_model.vocabulary.cum_table = old_model.cum_table

    new_model.train_count = old_model.train_count
    new_model.corpus_count = old_model.corpus_count
    new_model.running_training_loss = old_model.__dict__.get('running_training_loss', None)
    new_model.total_train_time = old_model.total_train_time
    new_model.min_alpha_yet_reached = old_model.min_alpha_yet_reached
    new_model.model_trimmed_post_training = old_model.__dict__.get('model_trimmed_post_training', None)

    return new_model