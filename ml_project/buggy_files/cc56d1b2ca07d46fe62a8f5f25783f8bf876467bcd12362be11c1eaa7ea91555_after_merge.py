    def train(ctx):
        if isinstance(ctx, mx.Context):
            ctx = [ctx]
        if opt.resume_params is '':
            net.initialize(mx.init.MSRAPrelu(), ctx=ctx)

        if opt.no_wd:
            for k, v in net.collect_params('.*beta|.*gamma|.*bias').items():
                v.wd_mult = 0.0

        compression_params = {
            "compressor": opt.compressor,
            "ef": opt.ef,
            "momentum": opt.compress_momentum,
            "scaling": opt.onebit_scaling,
            "k": opt.k
        }

        trainer = bps.DistributedTrainer(
            net.collect_params(), optimizer, optimizer_params, compression_params=compression_params)

        if opt.resume_states is not '':
            trainer.load_states(opt.resume_states)

        if opt.label_smoothing or opt.mixup:
            sparse_label_loss = False
        else:
            sparse_label_loss = True
        if distillation:
            L = gcv.loss.DistillationSoftmaxCrossEntropyLoss(temperature=opt.temperature,
                                                             hard_weight=opt.hard_weight,
                                                             sparse_label=sparse_label_loss)
        else:
            L = gluon.loss.SoftmaxCrossEntropyLoss(
                sparse_label=sparse_label_loss)

        best_val_score = 1

        for epoch in range(opt.resume_epoch, opt.num_epochs):
            tic = time.time()
            if opt.use_rec:
                train_data.reset()
            train_metric.reset()
            btic = time.time()

            for i, batch in enumerate(train_data):
                data, label = batch_fn(batch, ctx)

                if opt.mixup:
                    lam = np.random.beta(opt.mixup_alpha, opt.mixup_alpha)
                    if epoch >= opt.num_epochs - opt.mixup_off_epoch:
                        lam = 1
                    data = [lam*X + (1-lam)*X[::-1] for X in data]

                    if opt.label_smoothing:
                        eta = 0.1
                    else:
                        eta = 0.0
                    label = mixup_transform(label, classes, lam, eta)

                elif opt.label_smoothing:
                    hard_label = label
                    label = smooth(label, classes)

                if distillation:
                    teacher_prob = [nd.softmax(teacher(X.astype(opt.dtype, copy=False)) / opt.temperature)
                                    for X in data]

                with ag.record():
                    outputs = [net(X.astype(opt.dtype, copy=False))
                               for X in data]
                    if distillation:
                        loss = [L(yhat.astype('float32', copy=False),
                                  y.astype('float32', copy=False),
                                  p.astype('float32', copy=False)) for yhat, y, p in zip(outputs, label, teacher_prob)]
                    else:
                        loss = [L(yhat, y.astype(opt.dtype, copy=False))
                                for yhat, y in zip(outputs, label)]
                for l in loss:
                    l.backward()
                trainer.step(batch_size)

                if opt.mixup:
                    output_softmax = [nd.SoftmaxActivation(out.astype('float32', copy=False))
                                      for out in outputs]
                    train_metric.update(label, output_softmax)
                else:
                    if opt.label_smoothing:
                        train_metric.update(hard_label, outputs)
                    else:
                        train_metric.update(label, outputs)

                if opt.log_interval and not (i+1) % opt.log_interval:
                    train_metric_name, train_metric_score = train_metric.get()
                    logger.info('Epoch[%d] Batch [%d]\tSpeed: %f samples/sec\t%s=%f\tlr=%f\ttime=%f' % (
                                epoch, i, batch_size*nworker *
                                opt.log_interval/(time.time()-btic),
                                train_metric_name, train_metric_score, trainer.learning_rate, time.time()-btic))
                    btic = time.time()

            train_metric_name, train_metric_score = train_metric.get()
            throughput = int(batch_size * nworker * i / (time.time() - tic))

            logger.info('[Epoch %d] training: %s=%f' %
                        (epoch, train_metric_name, train_metric_score))
            logger.info('[Epoch %d] speed: %d samples/sec\ttime cost: %f' %
                        (epoch, throughput, time.time()-tic))

            err_top1_val, err_top5_val = test(ctx, val_data)

            logger.info('[Epoch %d] validation: err-top1=%f err-top5=%f' %
                        (epoch, err_top1_val, err_top5_val))

            if err_top1_val < best_val_score:
                best_val_score = err_top1_val
                net.save_parameters('%s/%.4f-imagenet-%s-%d-best.params' %
                                    (save_dir, best_val_score, model_name, epoch))
                trainer.save_states('%s/%.4f-imagenet-%s-%d-best.states' %
                                    (save_dir, best_val_score, model_name, epoch))

            if save_frequency and save_dir and (epoch + 1) % save_frequency == 0:
                net.save_parameters('%s/imagenet-%s-%d.params' %
                                    (save_dir, model_name, epoch))
                trainer.save_states('%s/imagenet-%s-%d.states' %
                                    (save_dir, model_name, epoch))

        if save_frequency and save_dir:
            net.save_parameters('%s/imagenet-%s-%d.params' %
                                (save_dir, model_name, opt.num_epochs-1))
            trainer.save_states('%s/imagenet-%s-%d.states' %
                                (save_dir, model_name, opt.num_epochs-1))