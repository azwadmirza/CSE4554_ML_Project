def create_data_iters_and_vocabs(args: argparse.Namespace,
                                 max_seq_len_source: int,
                                 max_seq_len_target: int,
                                 shared_vocab: bool,
                                 resume_training: bool,
                                 output_folder: str) -> Tuple['data_io.BaseParallelSampleIter',
                                                              'data_io.BaseParallelSampleIter',
                                                              'data_io.DataConfig',
                                                              List[vocab.Vocab], vocab.Vocab]:
    """
    Create the data iterators and the vocabularies.

    :param args: Arguments as returned by argparse.
    :param max_seq_len_source: Source maximum sequence length.
    :param max_seq_len_target: Target maximum sequence length.
    :param shared_vocab: Whether to create a shared vocabulary.
    :param resume_training: Whether to resume training.
    :param output_folder: Output folder.
    :return: The data iterators (train, validation, config_data) as well as the source and target vocabularies.
    """
    num_words_source, num_words_target = args.num_words
    num_words_source = num_words_source if num_words_source > 0 else None
    num_words_target = num_words_target if num_words_target > 0 else None

    word_min_count_source, word_min_count_target = args.word_min_count
    batch_num_devices = 1 if args.use_cpu else sum(-di if di < 0 else 1 for di in args.device_ids)
    batch_by_words = args.batch_type == C.BATCH_TYPE_WORD

    validation_sources = [args.validation_source] + args.validation_source_factors
    validation_sources = [str(os.path.abspath(source)) for source in validation_sources]

    either_raw_or_prepared_error_msg = "Either specify a raw training corpus with %s and %s or a preprocessed corpus " \
                                       "with %s." % (C.TRAINING_ARG_SOURCE,
                                                     C.TRAINING_ARG_TARGET,
                                                     C.TRAINING_ARG_PREPARED_DATA)
    if args.prepared_data is not None:
        utils.check_condition(args.source is None and args.target is None, either_raw_or_prepared_error_msg)
        if not resume_training:
            utils.check_condition(args.source_vocab is None and args.target_vocab is None,
                                  "You are using a prepared data folder, which is tied to a vocabulary. "
                                  "To change it you need to rerun data preparation with a different vocabulary.")
        train_iter, validation_iter, data_config, source_vocabs, target_vocab = data_io.get_prepared_data_iters(
            prepared_data_dir=args.prepared_data,
            validation_sources=validation_sources,
            validation_target=str(os.path.abspath(args.validation_target)),
            shared_vocab=shared_vocab,
            batch_size=args.batch_size,
            batch_by_words=batch_by_words,
            batch_num_devices=batch_num_devices,
            fill_up=args.fill_up)

        check_condition(len(source_vocabs) == len(args.source_factors_num_embed) + 1,
                        "Data was prepared with %d source factors, but only provided %d source factor dimensions." % (
                            len(source_vocabs), len(args.source_factors_num_embed) + 1))

        if resume_training:
            # resuming training. Making sure the vocabs in the model and in the prepared data match up
            model_source_vocabs = vocab.load_source_vocabs(output_folder)
            for i, (v, mv) in enumerate(zip(source_vocabs, model_source_vocabs)):
                utils.check_condition(vocab.are_identical(v, mv),
                                      "Prepared data and resumed model source vocab %d do not match." % i)
            model_target_vocab = vocab.load_target_vocab(output_folder)
            utils.check_condition(vocab.are_identical(target_vocab, model_target_vocab),
                                  "Prepared data and resumed model target vocabs do not match.")

        check_condition(data_config.num_source_factors == len(validation_sources),
                        'Training and validation data must have the same number of factors, but found %d and %d.' % (
                            data_config.num_source_factors, len(validation_sources)))

        return train_iter, validation_iter, data_config, source_vocabs, target_vocab

    else:
        utils.check_condition(args.prepared_data is None and args.source is not None and args.target is not None,
                              either_raw_or_prepared_error_msg)

        if resume_training:
            # Load the existing vocabs created when starting the training run.
            source_vocabs = vocab.load_source_vocabs(output_folder)
            target_vocab = vocab.load_target_vocab(output_folder)

            # Recover the vocabulary path from the data info file:
            data_info = cast(data_io.DataInfo, Config.load(os.path.join(output_folder, C.DATA_INFO)))
            source_vocab_paths = data_info.source_vocabs
            target_vocab_path = data_info.target_vocab

        else:
            # Load or create vocabs
            source_vocab_paths = [args.source_vocab] + [None] * len(args.source_factors)
            target_vocab_path = args.target_vocab
            source_vocabs, target_vocab = vocab.load_or_create_vocabs(
                source_paths=[args.source] + args.source_factors,
                target_path=args.target,
                source_vocab_paths=source_vocab_paths,
                target_vocab_path=target_vocab_path,
                shared_vocab=shared_vocab,
                num_words_source=num_words_source,
                num_words_target=num_words_target,
                word_min_count_source=word_min_count_source,
                word_min_count_target=word_min_count_target,
                pad_to_multiple_of=args.pad_vocab_to_multiple_of)

        check_condition(len(args.source_factors) == len(args.source_factors_num_embed),
                        "Number of source factor data (%d) differs from provided source factor dimensions (%d)" % (
                            len(args.source_factors), len(args.source_factors_num_embed)))

        sources = [args.source] + args.source_factors
        sources = [str(os.path.abspath(source)) for source in sources]

        check_condition(len(sources) == len(validation_sources),
                        'Training and validation data must have the same number of factors, but found %d and %d.' % (
                            len(source_vocabs), len(validation_sources)))

        train_iter, validation_iter, config_data, data_info = data_io.get_training_data_iters(
            sources=sources,
            target=os.path.abspath(args.target),
            validation_sources=validation_sources,
            validation_target=os.path.abspath(args.validation_target),
            source_vocabs=source_vocabs,
            target_vocab=target_vocab,
            source_vocab_paths=source_vocab_paths,
            target_vocab_path=target_vocab_path,
            shared_vocab=shared_vocab,
            batch_size=args.batch_size,
            batch_by_words=batch_by_words,
            batch_num_devices=batch_num_devices,
            fill_up=args.fill_up,
            max_seq_len_source=max_seq_len_source,
            max_seq_len_target=max_seq_len_target,
            bucketing=not args.no_bucketing,
            bucket_width=args.bucket_width)

        data_info_fname = os.path.join(output_folder, C.DATA_INFO)
        logger.info("Writing data config to '%s'", data_info_fname)
        data_info.save(data_info_fname)

        return train_iter, validation_iter, config_data, source_vocabs, target_vocab