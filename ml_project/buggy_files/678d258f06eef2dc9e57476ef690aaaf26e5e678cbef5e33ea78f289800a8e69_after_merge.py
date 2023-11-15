def train(lang, output_dir, train_data, dev_data, n_iter=30, n_sents=0,
         parser_multitasks='', entity_multitasks='',
          use_gpu=-1, vectors=None, no_tagger=False,
          no_parser=False, no_entities=False, gold_preproc=False,
          version="0.0.0", meta_path=None):
    """
    Train a model. Expects data in spaCy's JSON format.
    """
    util.fix_random_seed()
    util.set_env_log(True)
    n_sents = n_sents or None
    output_path = util.ensure_path(output_dir)
    train_path = util.ensure_path(train_data)
    dev_path = util.ensure_path(dev_data)
    meta_path = util.ensure_path(meta_path)
    if not output_path.exists():
        output_path.mkdir()
    if not train_path.exists():
        prints(train_path, title="Training data not found", exits=1)
    if dev_path and not dev_path.exists():
        prints(dev_path, title="Development data not found", exits=1)
    if meta_path is not None and not meta_path.exists():
        prints(meta_path, title="meta.json not found", exits=1)
    meta = util.read_json(meta_path) if meta_path else {}
    if not isinstance(meta, dict):
        prints("Expected dict but got: {}".format(type(meta)),
               title="Not a valid meta.json format", exits=1)
    meta.setdefault('lang', lang)
    meta.setdefault('name', 'unnamed')

    pipeline = ['tagger', 'parser', 'ner']
    if no_tagger and 'tagger' in pipeline:
        pipeline.remove('tagger')
    if no_parser and 'parser' in pipeline:
        pipeline.remove('parser')
    if no_entities and 'ner' in pipeline:
        pipeline.remove('ner')

    # Take dropout and batch size as generators of values -- dropout
    # starts high and decays sharply, to force the optimizer to explore.
    # Batch size starts at 1 and grows, so that we make updates quickly
    # at the beginning of training.
    dropout_rates = util.decaying(util.env_opt('dropout_from', 0.2),
                                  util.env_opt('dropout_to', 0.2),
                                  util.env_opt('dropout_decay', 0.0))
    batch_sizes = util.compounding(util.env_opt('batch_from', 1),
                                   util.env_opt('batch_to', 16),
                                   util.env_opt('batch_compound', 1.001))
    max_doc_len = util.env_opt('max_doc_len', 5000)
    corpus = GoldCorpus(train_path, dev_path, limit=n_sents)
    n_train_words = corpus.count_train()

    lang_class = util.get_lang_class(lang)
    nlp = lang_class()
    meta['pipeline'] = pipeline
    nlp.meta.update(meta)
    if vectors:
        print("Load vectors model", vectors)
        util.load_model(vectors, vocab=nlp.vocab)
        for lex in nlp.vocab:
            values = {}
            for attr, func in nlp.vocab.lex_attr_getters.items():
                # These attrs are expected to be set by data. Others should
                # be set by calling the language functions.
                if attr not in (CLUSTER, PROB, IS_OOV, LANG):
                    values[lex.vocab.strings[attr]] = func(lex.orth_)
            lex.set_attrs(**values)
            lex.is_oov = False
    for name in pipeline:
        nlp.add_pipe(nlp.create_pipe(name), name=name)
    if parser_multitasks:
        for objective in parser_multitasks.split(','):
            nlp.parser.add_multitask_objective(objective)
    if entity_multitasks:
        for objective in entity_multitasks.split(','):
            nlp.entity.add_multitask_objective(objective)
    optimizer = nlp.begin_training(lambda: corpus.train_tuples, device=use_gpu)
    nlp._optimizer = None

    print("Itn.\tP.Loss\tN.Loss\tUAS\tNER P.\tNER R.\tNER F.\tTag %\tToken %")
    try:
        train_docs = corpus.train_docs(nlp, projectivize=True, noise_level=0.0,
                                       gold_preproc=gold_preproc, max_length=0)
        train_docs = list(train_docs)
        for i in range(n_iter):
            with tqdm.tqdm(total=n_train_words, leave=False) as pbar:
                losses = {}
                for batch in minibatch(train_docs, size=batch_sizes):
                    batch = [(d, g) for (d, g) in batch if len(d) < max_doc_len]
                    if not batch:
                        continue
                    docs, golds = zip(*batch)
                    nlp.update(docs, golds, sgd=optimizer,
                               drop=next(dropout_rates), losses=losses)
                    pbar.update(sum(len(doc) for doc in docs))

            with nlp.use_params(optimizer.averages):
                util.set_env_log(False)
                epoch_model_path = output_path / ('model%d' % i)
                nlp.to_disk(epoch_model_path)
                nlp_loaded = util.load_model_from_path(epoch_model_path)
                dev_docs = list(corpus.dev_docs(
                                nlp_loaded,
                                gold_preproc=gold_preproc))
                nwords = sum(len(doc_gold[0]) for doc_gold in dev_docs)
                start_time = timer()
                scorer = nlp_loaded.evaluate(dev_docs)
                end_time = timer()
                if use_gpu < 0:
                    gpu_wps = None
                    cpu_wps = nwords/(end_time-start_time)
                else:
                    gpu_wps = nwords/(end_time-start_time)
                    with Model.use_device('cpu'):
                        nlp_loaded = util.load_model_from_path(epoch_model_path)
                        dev_docs = list(corpus.dev_docs(
                                        nlp_loaded, gold_preproc=gold_preproc))
                        start_time = timer()
                        scorer = nlp_loaded.evaluate(dev_docs)
                        end_time = timer()
                        cpu_wps = nwords/(end_time-start_time)
                acc_loc = (output_path / ('model%d' % i) / 'accuracy.json')
                with acc_loc.open('w') as file_:
                    file_.write(json_dumps(scorer.scores))
                meta_loc = output_path / ('model%d' % i) / 'meta.json'
                meta['accuracy'] = scorer.scores
                meta['speed'] = {'nwords': nwords, 'cpu': cpu_wps,
                                 'gpu': gpu_wps}
                meta['vectors'] = {'width': nlp.vocab.vectors_length,
                                   'vectors': len(nlp.vocab.vectors),
                                   'keys': nlp.vocab.vectors.n_keys}
                meta['lang'] = nlp.lang
                meta['pipeline'] = pipeline
                meta['spacy_version'] = '>=%s' % about.__version__
                meta.setdefault('name', 'model%d' % i)
                meta.setdefault('version', version)

                with meta_loc.open('w') as file_:
                    file_.write(json_dumps(meta))
                util.set_env_log(True)
            print_progress(i, losses, scorer.scores, cpu_wps=cpu_wps,
                           gpu_wps=gpu_wps)
    finally:
        print("Saving model...")
        with nlp.use_params(optimizer.averages):
            final_model_path = output_path / 'model-final'
            nlp.to_disk(final_model_path)