def train(args):
    """Train with the given args

    :param Namespace args: The program arguments
    """
    # display torch version
    logging.info('torch version = ' + torch.__version__)

    set_deterministic_pytorch(args)

    # check cuda and cudnn availability
    if not torch.cuda.is_available():
        logging.warning('cuda is not available')

    # get special label ids
    unk = args.char_list_dict['<unk>']
    eos = args.char_list_dict['<eos>']
    # read tokens as a sequence of sentences
    val, n_val_tokens, n_val_oovs = load_dataset(args.valid_label, args.char_list_dict, args.dump_hdf5_path)
    train, n_train_tokens, n_train_oovs = load_dataset(args.train_label, args.char_list_dict, args.dump_hdf5_path)
    logging.info('#vocab = ' + str(args.n_vocab))
    logging.info('#sentences in the training data = ' + str(len(train)))
    logging.info('#tokens in the training data = ' + str(n_train_tokens))
    logging.info('oov rate in the training data = %.2f %%' % (n_train_oovs / n_train_tokens * 100))
    logging.info('#sentences in the validation data = ' + str(len(val)))
    logging.info('#tokens in the validation data = ' + str(n_val_tokens))
    logging.info('oov rate in the validation data = %.2f %%' % (n_val_oovs / n_val_tokens * 100))

    use_sortagrad = args.sortagrad == -1 or args.sortagrad > 0
    # Create the dataset iterators
    batch_size = args.batchsize * max(args.ngpu, 1)
    if batch_size > args.batchsize:
        logging.info(f'batch size is automatically increased ({args.batchsize} -> {batch_size})')
    train_iter = ParallelSentenceIterator(train, batch_size,
                                          max_length=args.maxlen, sos=eos, eos=eos, shuffle=not use_sortagrad)
    val_iter = ParallelSentenceIterator(val, batch_size,
                                        max_length=args.maxlen, sos=eos, eos=eos, repeat=False)
    logging.info('#iterations per epoch = ' + str(len(train_iter.batch_indices)))
    logging.info('#total iterations = ' + str(args.epoch * len(train_iter.batch_indices)))
    # Prepare an RNNLM model
    rnn = RNNLM(args.n_vocab, args.layer, args.unit, args.type, args.dropout_rate)
    classifier = ClassifierWithState(rnn)
    reporter = classifier.reporter
    model = ReduceFramewiseLoss(classifier)
    if args.ngpu > 0:
        model = torch.nn.DataParallel(model, device_ids=list(range(args.ngpu))).cuda()
        setattr(model, "reporter", reporter)
        gpu_id = 0
    else:
        gpu_id = -1

    # Save model conf to json
    model_conf = args.outdir + '/model.json'
    with open(model_conf, 'wb') as f:
        logging.info('writing a model config file to ' + model_conf)
        f.write(json.dumps(vars(args), indent=4, ensure_ascii=False, sort_keys=True).encode('utf_8'))

    # Set up an optimizer
    if args.opt == 'sgd':
        optimizer = torch.optim.SGD(model.parameters(), lr=1.0)
    elif args.opt == 'adam':
        optimizer = torch.optim.Adam(model.parameters())

    # FIXME: TOO DIRTY HACK
    reporter = model.reporter
    setattr(optimizer, "target", reporter)
    setattr(optimizer, "serialize", lambda s: reporter.serialize(s))

    updater = BPTTUpdater(train_iter, model, optimizer, gpu_id, gradclip=args.gradclip)
    trainer = training.Trainer(updater, (args.epoch, 'epoch'), out=args.outdir)
    trainer.extend(LMEvaluator(val_iter, model, reporter, device=gpu_id))
    trainer.extend(extensions.LogReport(postprocess=compute_perplexity,
                                        trigger=(args.report_interval_iters, 'iteration')))
    trainer.extend(extensions.PrintReport(
        ['epoch', 'iteration', 'perplexity', 'val_perplexity', 'elapsed_time']
    ), trigger=(args.report_interval_iters, 'iteration'))
    trainer.extend(extensions.ProgressBar(update_interval=args.report_interval_iters))
    # Save best models
    trainer.extend(torch_snapshot(filename='snapshot.ep.{.updater.epoch}'))
    trainer.extend(snapshot_object(model, 'rnnlm.model.{.updater.epoch}'))
    # T.Hori: MinValueTrigger should be used, but it fails when resuming
    trainer.extend(MakeSymlinkToBestModel('validation/main/loss', 'rnnlm.model'))

    if use_sortagrad:
        trainer.extend(ShufflingEnabler([train_iter]),
                       trigger=(args.sortagrad if args.sortagrad != -1 else args.epoch, 'epoch'))
    if args.resume:
        logging.info('resumed from %s' % args.resume)
        torch_resume(args.resume, trainer)

    set_early_stop(trainer, args, is_lm=True)
    if args.tensorboard_dir is not None and args.tensorboard_dir != "":
        writer = SummaryWriter(args.tensorboard_dir)
        trainer.extend(TensorboardLogger(writer), trigger=(args.report_interval_iters, 'iteration'))

    trainer.run()
    check_early_stop(trainer, args.epoch)

    # compute perplexity for test set
    if args.test_label:
        logging.info('test the best model')
        torch_load(args.outdir + '/rnnlm.model.best', model)
        test = read_tokens(args.test_label, args.char_list_dict)
        n_test_tokens, n_test_oovs = count_tokens(test, unk)
        logging.info('#sentences in the test data = ' + str(len(test)))
        logging.info('#tokens in the test data = ' + str(n_test_tokens))
        logging.info('oov rate in the test data = %.2f %%' % (n_test_oovs / n_test_tokens * 100))
        test_iter = ParallelSentenceIterator(test, batch_size,
                                             max_length=args.maxlen, sos=eos, eos=eos, repeat=False)
        evaluator = LMEvaluator(test_iter, model, reporter, device=gpu_id)
        result = evaluator()
        logging.info('test perplexity: ' + str(np.exp(float(result['main/loss']))))