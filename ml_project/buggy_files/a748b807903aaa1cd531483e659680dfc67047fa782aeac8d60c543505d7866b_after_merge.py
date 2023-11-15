def train(args):
    # display chainer version
    logging.info('chainer version = ' + chainer.__version__)

    # seed setting (chainer seed may not need it)
    nseed = args.seed
    os.environ['CHAINER_SEED'] = str(nseed)
    logging.info('chainer seed = ' + os.environ['CHAINER_SEED'])

    # debug mode setting
    # 0 would be fastest, but 1 seems to be reasonable
    # by considering reproducability
    # revmoe type check
    if args.debugmode < 2:
        chainer.config.type_check = False
        logging.info('chainer type check is disabled')
    # use determinisitic computation or not
    if args.debugmode < 1:
        chainer.config.cudnn_deterministic = False
        logging.info('chainer cudnn deterministic is disabled')
    else:
        chainer.config.cudnn_deterministic = True

    # check cuda and cudnn availability
    if not chainer.cuda.available:
        logging.warning('cuda is not available')
    if not chainer.cuda.cudnn_enabled:
        logging.warning('cudnn is not available')

    with open(args.train_label, 'rb') as f:
        train = np.array([args.char_list_dict[char]
                          if char in args.char_list_dict else args.char_list_dict['<unk>']
                          for char in f.readline().decode('utf-8').split()], dtype=np.int32)
    with open(args.valid_label, 'rb') as f:
        valid = np.array([args.char_list_dict[char]
                          if char in args.char_list_dict else args.char_list_dict['<unk>']
                          for char in f.readline().decode('utf-8').split()], dtype=np.int32)

    logging.info('#vocab = ' + str(args.n_vocab))
    logging.info('#words in the training data = ' + str(len(train)))
    logging.info('#words in the validation data = ' + str(len(valid)))
    logging.info('#iterations per epoch = ' + str(len(train) // (args.batchsize * args.bproplen)))
    logging.info('#total iterations = ' + str(args.epoch * len(train) // (args.batchsize * args.bproplen)))

    # Create the dataset iterators
    train_iter = ParallelSequentialIterator(train, args.batchsize)
    valid_iter = ParallelSequentialIterator(valid, args.batchsize, repeat=False)

    # Prepare an RNNLM model
    rnn = RNNLM(args.n_vocab, args.unit)
    model = ClassifierWithState(rnn)
    model.compute_accuracy = False  # we only want the perplexity
    if args.ngpu > 1:
        logging.warn("currently, multi-gpu is not supported. use single gpu.")
    if args.ngpu > 0:
        # Make the specified GPU current
        gpu_id = 0
        chainer.cuda.get_device_from_id(gpu_id).use()
        model.to_gpu()
    else:
        gpu_id = -1

    # Save model conf to json
    model_conf = args.outdir + '/model.json'
    with open(model_conf, 'wb') as f:
        logging.info('writing a model config file to ' + model_conf)
        f.write(json.dumps(vars(args), indent=4, sort_keys=True).encode('utf_8'))

    # Set up an optimizer
    optimizer = chainer.optimizers.SGD(lr=1.0)
    optimizer.setup(model)
    optimizer.add_hook(chainer.optimizer.GradientClipping(args.gradclip))

    def evaluate(model, iter, bproplen=100):
        # Evaluation routine to be used for validation and test.
        model.predictor.train = False
        evaluator = model.copy()  # to use different state
        state = None
        evaluator.predictor.train = False  # dropout does nothing
        sum_perp = 0
        data_count = 0
        for batch in copy.copy(iter):
            x, t = convert.concat_examples(batch, gpu_id)
            state, loss = evaluator(state, x, t)
            sum_perp += loss.data
            if data_count % bproplen == 0:
                loss.unchain_backward()  # Truncate the graph
            data_count += 1
        model.predictor.train = True
        return np.exp(float(sum_perp) / data_count)

    sum_perp = 0
    count = 0
    iteration = 0
    epoch_now = 0
    best_valid = 100000000
    state = None
    while train_iter.epoch < args.epoch:
        loss = 0
        iteration += 1
        # Progress the dataset iterator for bprop_len words at each iteration.
        for i in range(args.bproplen):
            # Get the next batch (a list of tuples of two word IDs)
            batch = train_iter.__next__()
            # Concatenate the word IDs to matrices and send them to the device
            # self.converter does this job
            # (it is chainer.dataset.concat_examples by default)
            x, t = convert.concat_examples(batch, gpu_id)
            # Compute the loss at this time step and accumulate it
            state, loss_batch = optimizer.target(state, chainer.Variable(x), chainer.Variable(t))
            loss += loss_batch
            count += 1

        sum_perp += loss.data
        optimizer.target.cleargrads()  # Clear the parameter gradients
        loss.backward()  # Backprop
        loss.unchain_backward()  # Truncate the graph
        optimizer.update()  # Update the parameters

        if iteration % 100 == 0:
            logging.info('iteration: ' + str(iteration))
            logging.info('training perplexity: ' + str(np.exp(float(sum_perp) / count)))
            sum_perp = 0
            count = 0

        if train_iter.epoch > epoch_now:
            valid_perp = evaluate(model, valid_iter)
            logging.info('epoch: ' + str(train_iter.epoch))
            logging.info('validation perplexity: ' + str(valid_perp))

            # Save the model and the optimizer
            logging.info('save the model')
            serializers.save_npz(args.outdir + '/rnnlm.model.' + str(epoch_now), model)
            logging.info('save the optimizer')
            serializers.save_npz(args.outdir + '/rnnlm.state.' + str(epoch_now), optimizer)

            if valid_perp < best_valid:
                dest = args.outdir + '/rnnlm.model.best'
                if os.path.lexists(dest):
                    os.remove(dest)
                os.symlink('rnnlm.model.' + str(epoch_now), dest)
                best_valid = valid_perp

            epoch_now = train_iter.epoch