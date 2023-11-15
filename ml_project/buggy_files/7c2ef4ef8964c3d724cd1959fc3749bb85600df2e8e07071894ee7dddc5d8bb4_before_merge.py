def load_old_doc2vec(*args, **kwargs):
    old_model = Doc2Vec.load(*args, **kwargs)
    params = {
        'dm_mean': old_model.__dict__.get('dm_mean', None),
        'dm': old_model.dm,
        'dbow_words': old_model.dbow_words,
        'dm_concat': old_model.dm_concat,
        'dm_tag_count': old_model.dm_tag_count,
        'docvecs': old_model.__dict__.get('docvecs', None),
        'docvecs_mapfile': old_model.__dict__.get('docvecs_mapfile', None),
        'comment': old_model.__dict__.get('comment', None),
        'size': old_model.vector_size,
        'alpha': old_model.alpha,
        'window': old_model.window,
        'min_count': old_model.min_count,
        'max_vocab_size': old_model.__dict__.get('max_vocab_size', None),
        'sample': old_model.sample,
        'seed': old_model.seed,
        'workers': old_model.workers,
        'min_alpha': old_model.min_alpha,
        'hs': old_model.hs,
        'negative': old_model.negative,
        'cbow_mean': old_model.cbow_mean,
        'hashfxn': old_model.hashfxn,
        'iter': old_model.iter,
        'sorted_vocab': old_model.sorted_vocab,
        'batch_words': old_model.batch_words,
        'compute_loss': old_model.__dict__.get('compute_loss', None)
    }
    new_model = NewDoc2Vec(**params)
    # set word2vec trainables attributes
    new_model.wv.vectors = old_model.wv.syn0
    if hasattr(old_model.wv, 'syn0norm'):
        new_model.docvecs.vectors_norm = old_model.wv.syn0norm
    if hasattr(old_model, 'syn1'):
        new_model.trainables.syn1 = old_model.syn1
    if hasattr(old_model, 'syn1neg'):
        new_model.trainables.syn1neg = old_model.syn1neg
    if hasattr(old_model, 'syn0_lockf'):
        new_model.trainables.vectors_lockf = old_model.syn0_lockf

    # set doc2vec trainables attributes
    new_model.docvecs.vectors_docs = old_model.docvecs.doctag_syn0
    if hasattr(old_model.docvecs, 'doctag_syn0norm'):
        new_model.docvecs.vectors_docs_norm = old_model.docvecs.doctag_syn0norm
    if hasattr(old_model.docvecs, 'doctag_syn0_lockf'):
        new_model.trainables.vectors_docs_lockf = old_model.docvecs.doctag_syn0_lockf
    if hasattr(old_model.docvecs, 'mapfile_path'):
        new_model.docvecs.mapfile_path = old_model.docvecs.mapfile_path

    # set word2vec vocabulary attributes
    new_model.wv.vocab = old_model.wv.vocab
    new_model.wv.index2word = old_model.wv.index2word
    new_model.vocabulary.cum_table = old_model.cum_table

    # set doc2vec vocabulary attributes
    new_model.docvecs.doctags = old_model.docvecs.doctags
    new_model.docvecs.max_rawint = old_model.docvecs.max_rawint
    new_model.docvecs.offset2doctag = old_model.docvecs.offset2doctag
    new_model.docvecs.count = old_model.docvecs.count

    new_model.train_count = old_model.train_count
    new_model.corpus_count = old_model.corpus_count
    new_model.running_training_loss = old_model.running_training_loss
    new_model.total_train_time = old_model.total_train_time
    new_model.min_alpha_yet_reached = old_model.min_alpha_yet_reached
    new_model.model_trimmed_post_training = old_model.model_trimmed_post_training

    return new_model