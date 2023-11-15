def train(
    lang,
    output_path,
    train_path,
    dev_path,
    raw_text=None,
    base_model=None,
    pipeline="tagger,parser,ner",
    replace_components=False,
    vectors=None,
    width=96,
    conv_depth=4,
    cnn_window=1,
    cnn_pieces=3,
    use_chars=False,
    bilstm_depth=0,
    embed_rows=2000,
    n_iter=30,
    n_early_stopping=None,
    n_examples=0,
    use_gpu=-1,
    version="0.0.0",
    meta_path=None,
    init_tok2vec=None,
    parser_multitasks="",
    entity_multitasks="",
    noise_level=0.0,
    orth_variant_level=0.0,
    eval_beam_widths="",
    gold_preproc=False,
    learn_tokens=False,
    textcat_multilabel=False,
    textcat_arch="bow",
    textcat_positive_label=None,
    tag_map_path=None,
    verbose=False,
    debug=False,
):
    """
    Train or update a spaCy model. Requires data to be formatted in spaCy's
    JSON format. To convert data from other formats, use the `spacy convert`
    command.
    """
    util.fix_random_seed()
    util.set_env_log(verbose)

    # Make sure all files and paths exists if they are needed
    train_path = util.ensure_path(train_path)
    dev_path = util.ensure_path(dev_path)
    meta_path = util.ensure_path(meta_path)
    output_path = util.ensure_path(output_path)
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
        msg.good("Created output directory: {}".format(output_path))

    tag_map = {}
    if tag_map_path is not None:
        tag_map = srsly.read_json(tag_map_path)
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

    if not eval_beam_widths:
        eval_beam_widths = [1]
    else:
        eval_beam_widths = [int(bw) for bw in eval_beam_widths.split(",")]
        if 1 not in eval_beam_widths:
            eval_beam_widths.append(1)
        eval_beam_widths.sort()
    has_beam_widths = eval_beam_widths != [1]

    # Set up the base model and pipeline. If a base model is specified, load
    # the model and make sure the pipeline matches the pipeline setting. If
    # training starts from a blank model, intitalize the language class.
    pipeline = [p.strip() for p in pipeline.split(",")]
    disabled_pipes = None
    pipes_added = False
    msg.text("Training pipeline: {}".format(pipeline))
    if use_gpu >= 0:
        activated_gpu = None
        try:
            activated_gpu = set_gpu(use_gpu)
        except Exception as e:
            msg.warn("Exception: {}".format(e))
        if activated_gpu is not None:
            msg.text("Using GPU: {}".format(use_gpu))
        else:
            msg.warn("Unable to activate GPU: {}".format(use_gpu))
            msg.text("Using CPU only")
            use_gpu = -1
    if base_model:
        msg.text("Starting with base model '{}'".format(base_model))
        nlp = util.load_model(base_model)
        if nlp.lang != lang:
            msg.fail(
                "Model language ('{}') doesn't match language specified as "
                "`lang` argument ('{}') ".format(nlp.lang, lang),
                exits=1,
            )
        for pipe in pipeline:
            pipe_cfg = {}
            if pipe == "parser":
                pipe_cfg = {"learn_tokens": learn_tokens}
            elif pipe == "textcat":
                pipe_cfg = {
                    "exclusive_classes": not textcat_multilabel,
                    "architecture": textcat_arch,
                    "positive_label": textcat_positive_label,
                }
            if pipe not in nlp.pipe_names:
                msg.text("Adding component to base model '{}'".format(pipe))
                nlp.add_pipe(nlp.create_pipe(pipe, config=pipe_cfg))
                pipes_added = True
            elif replace_components:
                msg.text("Replacing component from base model '{}'".format(pipe))
                nlp.replace_pipe(pipe, nlp.create_pipe(pipe, config=pipe_cfg))
                pipes_added = True
            else:
                if pipe == "textcat":
                    textcat_cfg = nlp.get_pipe("textcat").cfg
                    base_cfg = {
                        "exclusive_classes": textcat_cfg["exclusive_classes"],
                        "architecture": textcat_cfg["architecture"],
                        "positive_label": textcat_cfg["positive_label"],
                    }
                    if base_cfg != pipe_cfg:
                        msg.fail(
                            "The base textcat model configuration does"
                            "not match the provided training options. "
                            "Existing cfg: {}, provided cfg: {}".format(
                                base_cfg, pipe_cfg
                            ),
                            exits=1,
                        )
                msg.text("Extending component from base model '{}'".format(pipe))
        disabled_pipes = nlp.disable_pipes(
            [p for p in nlp.pipe_names if p not in pipeline]
        )
    else:
        msg.text("Starting with blank model '{}'".format(lang))
        lang_cls = util.get_lang_class(lang)
        nlp = lang_cls()
        for pipe in pipeline:
            if pipe == "parser":
                pipe_cfg = {"learn_tokens": learn_tokens}
            elif pipe == "textcat":
                pipe_cfg = {
                    "exclusive_classes": not textcat_multilabel,
                    "architecture": textcat_arch,
                    "positive_label": textcat_positive_label,
                }
            else:
                pipe_cfg = {}
            nlp.add_pipe(nlp.create_pipe(pipe, config=pipe_cfg))

    # Update tag map with provided mapping
    nlp.vocab.morphology.tag_map.update(tag_map)

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

    if base_model and not pipes_added:
        # Start with an existing model, use default optimizer
        optimizer = create_default_optimizer(Model.ops)
    else:
        # Start with a blank model, call begin_training
        cfg = {"device": use_gpu}
        cfg["conv_depth"] = conv_depth
        cfg["token_vector_width"] = width
        cfg["bilstm_depth"] = bilstm_depth
        cfg["cnn_maxout_pieces"] = cnn_pieces
        cfg["embed_size"] = embed_rows
        cfg["conv_window"] = cnn_window
        cfg["subword_features"] = not use_chars
        optimizer = nlp.begin_training(lambda: corpus.train_tuples, **cfg)

    nlp._optimizer = None

    # Load in pretrained weights
    if init_tok2vec is not None:
        components = _load_pretrained_tok2vec(nlp, init_tok2vec)
        msg.text("Loaded pretrained tok2vec for: {}".format(components))

    # Verify textcat config
    if "textcat" in pipeline:
        textcat_labels = nlp.get_pipe("textcat").cfg.get("labels", [])
        if textcat_positive_label and textcat_positive_label not in textcat_labels:
            msg.fail(
                "The textcat_positive_label (tpl) '{}' does not match any "
                "label in the training data.".format(textcat_positive_label),
                exits=1,
            )
        if textcat_positive_label and len(textcat_labels) != 2:
            msg.fail(
                "A textcat_positive_label (tpl) '{}' was provided for training "
                "data that does not appear to be a binary classification "
                "problem with two labels.".format(textcat_positive_label),
                exits=1,
            )
        train_docs = corpus.train_docs(
            nlp,
            noise_level=noise_level,
            gold_preproc=gold_preproc,
            max_length=0,
            ignore_misaligned=True,
        )
        train_labels = set()
        if textcat_multilabel:
            multilabel_found = False
            for text, gold in train_docs:
                train_labels.update(gold.cats.keys())
                if list(gold.cats.values()).count(1.0) != 1:
                    multilabel_found = True
            if not multilabel_found and not base_model:
                msg.warn(
                    "The textcat training instances look like they have "
                    "mutually-exclusive classes. Remove the flag "
                    "'--textcat-multilabel' to train a classifier with "
                    "mutually-exclusive classes."
                )
        if not textcat_multilabel:
            for text, gold in train_docs:
                train_labels.update(gold.cats.keys())
                if list(gold.cats.values()).count(1.0) != 1 and not base_model:
                    msg.warn(
                        "Some textcat training instances do not have exactly "
                        "one positive label. Modifying training options to "
                        "include the flag '--textcat-multilabel' for classes "
                        "that are not mutually exclusive."
                    )
                    nlp.get_pipe("textcat").cfg["exclusive_classes"] = False
                    textcat_multilabel = True
                    break
        if base_model and set(textcat_labels) != train_labels:
            msg.fail(
                "Cannot extend textcat model using data with different "
                "labels. Base model labels: {}, training data labels: "
                "{}.".format(textcat_labels, list(train_labels)),
                exits=1,
            )
        if textcat_multilabel:
            msg.text(
                "Textcat evaluation score: ROC AUC score macro-averaged across "
                "the labels '{}'".format(", ".join(textcat_labels))
            )
        elif textcat_positive_label and len(textcat_labels) == 2:
            msg.text(
                "Textcat evaluation score: F1-score for the "
                "label '{}'".format(textcat_positive_label)
            )
        elif len(textcat_labels) > 1:
            if len(textcat_labels) == 2:
                msg.warn(
                    "If the textcat component is a binary classifier with "
                    "exclusive classes, provide '--textcat_positive_label' for "
                    "an evaluation on the positive class."
                )
            msg.text(
                "Textcat evaluation score: F1-score macro-averaged across "
                "the labels '{}'".format(", ".join(textcat_labels))
            )
        else:
            msg.fail(
                "Unsupported textcat configuration. Use `spacy debug-data` "
                "for more information."
            )

    # fmt: off
    row_head, output_stats = _configure_training_output(pipeline, use_gpu, has_beam_widths)
    row_widths = [len(w) for w in row_head]
    row_settings = {"widths": row_widths, "aligns": tuple(["r" for i in row_head]), "spacing": 2}
    # fmt: on
    print("")
    msg.row(row_head, **row_settings)
    msg.row(["-" * width for width in row_settings["widths"]], **row_settings)
    try:
        iter_since_best = 0
        best_score = 0.0
        for i in range(n_iter):
            train_docs = corpus.train_docs(
                nlp,
                noise_level=noise_level,
                orth_variant_level=orth_variant_level,
                gold_preproc=gold_preproc,
                max_length=0,
                ignore_misaligned=True,
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
                    try:
                        nlp.update(
                            docs,
                            golds,
                            sgd=optimizer,
                            drop=next(dropout_rates),
                            losses=losses,
                        )
                    except ValueError as e:
                        err = "Error during training"
                        if init_tok2vec:
                            err += " Did you provide the same parameters during 'train' as during 'pretrain'?"
                        msg.fail(err, "Original error message: {}".format(e), exits=1)
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
                for beam_width in eval_beam_widths:
                    for name, component in nlp_loaded.pipeline:
                        if hasattr(component, "cfg"):
                            component.cfg["beam_width"] = beam_width
                    dev_docs = list(
                        corpus.dev_docs(
                            nlp_loaded,
                            gold_preproc=gold_preproc,
                            ignore_misaligned=True,
                        )
                    )
                    nwords = sum(len(doc_gold[0]) for doc_gold in dev_docs)
                    start_time = timer()
                    scorer = nlp_loaded.evaluate(dev_docs, verbose=verbose)
                    end_time = timer()
                    if use_gpu < 0:
                        gpu_wps = None
                        cpu_wps = nwords / (end_time - start_time)
                    else:
                        gpu_wps = nwords / (end_time - start_time)
                        with Model.use_device("cpu"):
                            nlp_loaded = util.load_model_from_path(epoch_model_path)
                            for name, component in nlp_loaded.pipeline:
                                if hasattr(component, "cfg"):
                                    component.cfg["beam_width"] = beam_width
                            dev_docs = list(
                                corpus.dev_docs(
                                    nlp_loaded,
                                    gold_preproc=gold_preproc,
                                    ignore_misaligned=True,
                                )
                            )
                            start_time = timer()
                            scorer = nlp_loaded.evaluate(dev_docs, verbose=verbose)
                            end_time = timer()
                            cpu_wps = nwords / (end_time - start_time)
                    acc_loc = output_path / ("model%d" % i) / "accuracy.json"
                    srsly.write_json(acc_loc, scorer.scores)

                    # Update model meta.json
                    meta["lang"] = nlp.lang
                    meta["pipeline"] = nlp.pipe_names
                    meta["spacy_version"] = ">=%s" % about.__version__
                    if beam_width == 1:
                        meta["speed"] = {
                            "nwords": nwords,
                            "cpu": cpu_wps,
                            "gpu": gpu_wps,
                        }
                        meta.setdefault("accuracy", {})
                        for component in nlp.pipe_names:
                            for metric in _get_metrics(component):
                                meta["accuracy"][metric] = scorer.scores[metric]
                    else:
                        meta.setdefault("beam_accuracy", {})
                        meta.setdefault("beam_speed", {})
                        for component in nlp.pipe_names:
                            for metric in _get_metrics(component):
                                meta["beam_accuracy"][metric] = scorer.scores[metric]
                        meta["beam_speed"][beam_width] = {
                            "nwords": nwords,
                            "cpu": cpu_wps,
                            "gpu": gpu_wps,
                        }
                    meta["vectors"] = {
                        "width": nlp.vocab.vectors_length,
                        "vectors": len(nlp.vocab.vectors),
                        "keys": nlp.vocab.vectors.n_keys,
                        "name": nlp.vocab.vectors.name,
                    }
                    meta.setdefault("name", "model%d" % i)
                    meta.setdefault("version", version)
                    meta["labels"] = nlp.meta["labels"]
                    meta_loc = output_path / ("model%d" % i) / "meta.json"
                    srsly.write_json(meta_loc, meta)
                    util.set_env_log(verbose)

                    progress = _get_progress(
                        i,
                        losses,
                        scorer.scores,
                        output_stats,
                        beam_width=beam_width if has_beam_widths else None,
                        cpu_wps=cpu_wps,
                        gpu_wps=gpu_wps,
                    )
                    if i == 0 and "textcat" in pipeline:
                        textcats_per_cat = scorer.scores.get("textcats_per_cat", {})
                        for cat, cat_score in textcats_per_cat.items():
                            if cat_score.get("roc_auc_score", 0) < 0:
                                msg.warn(
                                    "Textcat ROC AUC score is undefined due to "
                                    "only one value in label '{}'.".format(cat)
                                )
                    msg.row(progress, **row_settings)
                # Early stopping
                if n_early_stopping is not None:
                    current_score = _score_for_model(meta)
                    if current_score < best_score:
                        iter_since_best += 1
                    else:
                        iter_since_best = 0
                        best_score = current_score
                    if iter_since_best >= n_early_stopping:
                        msg.text(
                            "Early stopping, best iteration "
                            "is: {}".format(i - iter_since_best)
                        )
                        msg.text(
                            "Best score = {}; Final iteration "
                            "score = {}".format(best_score, current_score)
                        )
                        break
    except Exception as e:
        msg.warn(
            "Aborting and saving the final best model. "
            "Encountered exception: {}".format(e)
        )
    finally:
        best_pipes = nlp.pipe_names
        if disabled_pipes:
            disabled_pipes.restore()
        with nlp.use_params(optimizer.averages):
            final_model_path = output_path / "model-final"
            nlp.to_disk(final_model_path)
            meta_loc = output_path / "model-final" / "meta.json"
            final_meta = srsly.read_json(meta_loc)
            final_meta.setdefault("accuracy", {})
            final_meta["accuracy"].update(meta.get("accuracy", {}))
            final_meta.setdefault("speed", {})
            final_meta["speed"].setdefault("cpu", None)
            final_meta["speed"].setdefault("gpu", None)
            # combine cpu and gpu speeds with the base model speeds
            if final_meta["speed"]["cpu"] and meta["speed"]["cpu"]:
                speed = _get_total_speed(
                    [final_meta["speed"]["cpu"], meta["speed"]["cpu"]]
                )
                final_meta["speed"]["cpu"] = speed
            if final_meta["speed"]["gpu"] and meta["speed"]["gpu"]:
                speed = _get_total_speed(
                    [final_meta["speed"]["gpu"], meta["speed"]["gpu"]]
                )
                final_meta["speed"]["gpu"] = speed
            # if there were no speeds to update, overwrite with meta
            if (
                final_meta["speed"]["cpu"] is None
                and final_meta["speed"]["gpu"] is None
            ):
                final_meta["speed"].update(meta["speed"])
            # note: beam speeds are not combined with the base model
            if has_beam_widths:
                final_meta.setdefault("beam_accuracy", {})
                final_meta["beam_accuracy"].update(meta.get("beam_accuracy", {}))
                final_meta.setdefault("beam_speed", {})
                final_meta["beam_speed"].update(meta.get("beam_speed", {}))
            srsly.write_json(meta_loc, final_meta)
        msg.good("Saved model to output directory", final_model_path)
        with msg.loading("Creating best model..."):
            best_model_path = _collate_best_model(final_meta, output_path, best_pipes)
        msg.good("Created best model", best_model_path)