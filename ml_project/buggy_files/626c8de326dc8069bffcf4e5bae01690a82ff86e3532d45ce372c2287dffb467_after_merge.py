def load_old_doc2vec(*args, **kwargs):
    old_model = Doc2Vec.load(*args, **kwargs)
    params = {
        'dm_mean': old_model.__dict__.get('dm_mean', None),
        'dm': old_model.dm,
        'dbow_words': old_model.dbow_words,
        'dm_concat': old_model.dm_concat,
        'dm_tag_count': old_model.dm_tag_count,
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
        'sorted_vocab': old_model.__dict__.get('sorted_vocab', 1),
        'batch_words': old_model.__dict__.get('batch_words', MAX_WORDS_IN_BATCH),
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
    new_model.docvecs.count = old_model.docvecs.count
    if hasattr(old_model.docvecs, 'max_rawint'):  # `doc2vec` models before `0.12.3` do not have these 2 attributes
        new_model.docvecs.max_rawint = old_model.docvecs.__dict__.get('max_rawint')
        new_model.docvecs.offset2doctag = old_model.docvecs.__dict__.get('offset2doctag')
    else:
        # Doc2Vec models before Gensim version 0.12.3 did not have `max_rawint` and `offset2doctag` as they did not
        # mixing of string and int tags. This implies the new attribute `offset2doctag` equals the old `index2doctag`
        # (which was only filled if the documents had string tags).
        # This also implies that the new attribute, `max_rawint`(highest rawint-indexed doctag) would either be equal
        # to the initial value -1, in case only string tags are used or would be equal to `count` if only int indexing
        # was used.
        new_model.docvecs.max_rawint = -1 if old_model.docvecs.index2doctag else old_model.docvecs.count - 1
        new_model.docvecs.offset2doctag = old_model.docvecs.index2doctag

    new_model.train_count = old_model.__dict__.get('train_count', None)
    new_model.corpus_count = old_model.__dict__.get('corpus_count', None)
    new_model.running_training_loss = old_model.__dict__.get('running_training_loss', 0)
    new_model.total_train_time = old_model.__dict__.get('total_train_time', None)
    new_model.min_alpha_yet_reached = old_model.__dict__.get('min_alpha_yet_reached', old_model.alpha)
    new_model.model_trimmed_post_training = old_model.__dict__.get('model_trimmed_post_training', None)

    return new_model