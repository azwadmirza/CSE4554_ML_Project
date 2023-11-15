def train(
    lang,
    output_path,
    train_path,
    dev_path,
    raw_text=None,
    base_model=None,
    pipeline="tagger,parser,ner",
    vectors=None,
    n_iter=30,
    n_examples=0,
    use_gpu=-1,
    version="0.0.0",
    meta_path=None,
    init_tok2vec=None,
    parser_multitasks="",
    entity_multitasks="",
    noise_level=0.0,
    gold_preproc=False,
    learn_tokens=False,
    verbose=False,
    debug=False,
):
    """
    Train or update a spaCy model. Requires data to be formatted in spaCy's
    JSON format. To convert data from other formats, use the `spacy convert`
    command.
    """
    msg = Printer()
    util.fix_random_seed()
    util.set_env_log(verbose)

    # Make sure all files and paths exists if they are needed
    train_path = util.ensure_path(train_path)
    dev_path = util.ensure_path(dev_path)
    meta_path = util.ensure_path(meta_path)
    if raw_text is not None:
        raw_text = list(srsly.read_jsonl(raw_text))
    if not train_path or not train_path.exists():
        msg.fail("Training data not found", train_path, exits=1)
    if not dev_path or not dev_path.exists():
        msg.fail("Development data not found", dev_path, exits=1)
    if meta_path is not None and not meta_path.exists():
        msg.fail("Can't find model meta.json", meta_path, exits=1)
    meta = srsly.read_json(meta_path) if meta_path else {}
    if output_path.exists() and [p for p in output_path.iterdir() if p.is_dir()]:
        msg.warn(
            "Output directory is not empty",
            "This can lead to unintended side effects when saving the model. "
            "Please use an empty directory or a different path instead. If "
            "the specified output path doesn't exist, the directory will be "
            "created for you.",
        )
    if not output_path.exists():
        output_path.mkdir()

    # Take dropout and batch size as generators of values -- dropout
    # starts high and decays sharply, to force the optimizer to explore.
    # Batch size starts at 1 and grows, so that we make updates quickly
    # at the beginning of training.
    dropout_rates = util.decaying(
        util.env_opt("dropout_from", 0.2),
        util.env_opt("dropout_to", 0.2),
        util.env_opt("dropout_decay", 0.0),
    )
    batch_sizes = util.compounding(
        util.env_opt("batch_from", 100.0),
        util.env_opt("batch_to", 1000.0),
        util.env_opt("batch_compound", 1.001),
    )

    # Set up the base model and pipeline. If a base model is specified, load
    # the model and make sure the pipeline matches the pipeline setting. If
    # training starts from a blank model, intitalize the language class.
    pipeline = [p.strip() for p in pipeline.split(",")]
    msg.text("Training pipeline: {}".format(pipeline))
    if base_model:
        msg.text("Starting with base model '{}'".format(base_model))
        nlp = util.load_model(base_model)
        if nlp.lang != lang:
            msg.fail(
                "Model language ('{}') doesn't match language specified as "
                "`lang` argument ('{}') ".format(nlp.lang, lang),
                exits=1,
            )
        other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipeline]
        nlp.disable_pipes(*other_pipes)
        for pipe in pipeline:
            if pipe not in nlp.pipe_names:
                nlp.add_pipe(nlp.create_pipe(pipe))
    else:
        msg.text("Starting with blank model '{}'".format(lang))
        lang_cls = util.get_lang_class(lang)
        nlp = lang_cls()
        for pipe in pipeline:
            nlp.add_pipe(nlp.create_pipe(pipe))

    if learn_tokens:
        nlp.add_pipe(nlp.create_pipe("merge_subtokens"))

    if vectors:
        msg.text("Loading vector from model '{}'".format(vectors))
        _load_vectors(nlp, vectors)

    # Multitask objectives
    multitask_options = [("parser", parser_multitasks), ("ner", entity_multitasks)]
    for pipe_name, multitasks in multitask_options:
        if multitasks:
            if pipe_name not in pipeline:
                msg.fail(
                    "Can't use multitask objective without '{}' in the "
                    "pipeline".format(pipe_name)
                )
            pipe = nlp.get_pipe(pipe_name)
            for objective in multitasks.split(","):
                pipe.add_multitask_objective(objective)

    # Prepare training corpus
    msg.text("Counting training words (limit={})".format(n_examples))
    corpus = GoldCorpus(train_path, dev_path, limit=n_examples)
    n_train_words = corpus.count_train()

    if base_model:
        # Start with an existing model, use default optimizer
        optimizer = create_default_optimizer(Model.ops)
    else:
        # Start with a blank model, call begin_training
        optimizer = nlp.begin_training(lambda: corpus.train_tuples, device=use_gpu)

    nlp._optimizer = None

    # Load in pre-trained weights
    if init_tok2vec is not None:
        components = _load_pretrained_tok2vec(nlp, init_tok2vec)
        msg.text("Loaded pretrained tok2vec for: {}".format(components))

    # fmt: off
    row_head = ("Itn", "Dep Loss", "NER Loss", "UAS", "NER P", "NER R", "NER F", "Tag %", "Token %", "CPU WPS", "GPU WPS")
    row_settings = {
        "widths": (3, 10, 10, 7, 7, 7, 7, 7, 7, 7, 7),
        "aligns": tuple(["r" for i in row_head]),
        "spacing": 2
    }
    # fmt: on
    print("")
    msg.row(row_head, **row_settings)
    msg.row(["-" * width for width in row_settings["widths"]], **row_settings)
    try:
        for i in range(n_iter):
            train_docs = corpus.train_docs(
                nlp, noise_level=noise_level, gold_preproc=gold_preproc, max_length=0
            )
            if raw_text:
                random.shuffle(raw_text)
                raw_batches = util.minibatch(
                    (nlp.make_doc(rt["text"]) for rt in raw_text), size=8
                )
            words_seen = 0
            with tqdm.tqdm(total=n_train_words, leave=False) as pbar:
                losses = {}
                for batch in util.minibatch_by_words(train_docs, size=batch_sizes):
                    if not batch:
                        continue
                    docs, golds = zip(*batch)
                    nlp.update(
                        docs,
                        golds,
                        sgd=optimizer,
                        drop=next(dropout_rates),
                        losses=losses,
                    )
                    if raw_text:
                        # If raw text is available, perform 'rehearsal' updates,
                        # which use unlabelled data to reduce overfitting.
                        raw_batch = list(next(raw_batches))
                        nlp.rehearse(raw_batch, sgd=optimizer, losses=losses)
                    if not int(os.environ.get("LOG_FRIENDLY", 0)):
                        pbar.update(sum(len(doc) for doc in docs))
                    words_seen += sum(len(doc) for doc in docs)
            with nlp.use_params(optimizer.averages):
                util.set_env_log(False)
                epoch_model_path = output_path / ("model%d" % i)
                nlp.to_disk(epoch_model_path)
                nlp_loaded = util.load_model_from_path(epoch_model_path)
                dev_docs = list(corpus.dev_docs(nlp_loaded, gold_preproc=gold_preproc))
                nwords = sum(len(doc_gold[0]) for doc_gold in dev_docs)
                start_time = timer()
                scorer = nlp_loaded.evaluate(dev_docs, debug)
                end_time = timer()
                if use_gpu < 0:
                    gpu_wps = None
                    cpu_wps = nwords / (end_time - start_time)
                else:
                    gpu_wps = nwords / (end_time - start_time)
                    with Model.use_device("cpu"):
                        nlp_loaded = util.load_model_from_path(epoch_model_path)
                        dev_docs = list(
                            corpus.dev_docs(nlp_loaded, gold_preproc=gold_preproc)
                        )
                        start_time = timer()
                        scorer = nlp_loaded.evaluate(dev_docs)
                        end_time = timer()
                        cpu_wps = nwords / (end_time - start_time)
                acc_loc = output_path / ("model%d" % i) / "accuracy.json"
                srsly.write_json(acc_loc, scorer.scores)

                # Update model meta.json
                meta["lang"] = nlp.lang
                meta["pipeline"] = nlp.pipe_names
                meta["spacy_version"] = ">=%s" % about.__version__
                meta["accuracy"] = scorer.scores
                meta["speed"] = {"nwords": nwords, "cpu": cpu_wps, "gpu": gpu_wps}
                meta["vectors"] = {
                    "width": nlp.vocab.vectors_length,
                    "vectors": len(nlp.vocab.vectors),
                    "keys": nlp.vocab.vectors.n_keys,
                    "name": nlp.vocab.vectors.name
                }
                meta.setdefault("name", "model%d" % i)
                meta.setdefault("version", version)
                meta_loc = output_path / ("model%d" % i) / "meta.json"
                srsly.write_json(meta_loc, meta)

                util.set_env_log(verbose)

            progress = _get_progress(
                i, losses, scorer.scores, cpu_wps=cpu_wps, gpu_wps=gpu_wps
            )
            msg.row(progress, **row_settings)
    finally:
        with nlp.use_params(optimizer.averages):
            final_model_path = output_path / "model-final"
            nlp.to_disk(final_model_path)
        msg.good("Saved model to output directory", final_model_path)
        with msg.loading("Creating best model..."):
            best_model_path = _collate_best_model(meta, output_path, nlp.pipe_names)
        msg.good("Created best model", best_model_path)