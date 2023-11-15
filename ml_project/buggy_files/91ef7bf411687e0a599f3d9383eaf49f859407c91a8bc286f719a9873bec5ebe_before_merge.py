def train():
    """Training loop for awd language model.

    """
    ntasgd = False
    best_val = float('Inf')
    start_train_time = time.time()
    parameters = model.collect_params()
    param_dict_avg = None
    t = 0
    avg_trigger = 0
    n = 5
    valid_losses = []
    for epoch in range(args.epochs):
        total_L = 0.0
        start_epoch_time = time.time()
        start_log_interval_time = time.time()
        hiddens = [model.begin_state(args.batch_size//len(context),
                                     func=mx.nd.zeros, ctx=ctx) for ctx in context]
        batch_i, i = 0, 0
        while i < len(train_data) - 1 - 1:
            bptt = args.bptt if mx.nd.random.uniform().asscalar() < 0.95 else args.bptt / 2
            seq_len = max(5, int(mx.nd.random.normal(bptt, 5).asscalar()))
            lr_batch_start = trainer.learning_rate
            trainer.set_learning_rate(lr_batch_start*seq_len/args.bptt)

            data, target = get_batch(train_data, i, seq_len=seq_len)
            data_list = gluon.utils.split_and_load(data, context, batch_axis=1, even_split=True)
            target_list = gluon.utils.split_and_load(target, context, batch_axis=1, even_split=True)
            hiddens = detach(hiddens)
            Ls = []
            with autograd.record():
                for j, (X, y, h) in enumerate(zip(data_list, target_list, hiddens)):
                    output, h, encoder_hs, dropped_encoder_hs = model(X, h)
                    l = joint_loss(output, y, encoder_hs, dropped_encoder_hs)
                    Ls.append(l / (len(context) * X.size))
                    hiddens[j] = h
            for L in Ls:
                L.backward()

            grads = [p.grad(d.context) for p in parameters.values() for d in data_list]
            gluon.utils.clip_global_norm(grads, args.clip)

            if args.ntasgd and ntasgd:
                if param_dict_avg is None:
                    param_dict_avg = {k.split(model._prefix)[1]: v.data(context[0]).copy()
                                      for k, v in parameters.items()}

            trainer.step(1)

            if args.ntasgd and ntasgd:
                gamma = 1.0 / max(1, epoch * (len(train_data) // args.bptt)
                                  + batch_i - avg_trigger + 2)
                for name, param_avg in param_dict_avg.items():
                    param_avg[:] += gamma * (parameters['{}{}'.format(model._prefix, name)]
                                             .data(context[0]) - param_avg)

            total_L += sum([mx.nd.sum(L).asscalar() for L in Ls])
            trainer.set_learning_rate(lr_batch_start)

            if batch_i % args.log_interval == 0 and batch_i > 0:
                cur_L = total_L / args.log_interval
                print('[Epoch %d Batch %d/%d] current loss %.2f, ppl %.2f, '
                      'throughput %.2f samples/s, lr %.2f'
                      % (epoch, batch_i, len(train_data) // args.bptt, cur_L, math.exp(cur_L),
                         args.batch_size * args.log_interval
                         / (time.time() - start_log_interval_time),
                         lr_batch_start * seq_len / args.bptt))
                total_L = 0.0
                start_log_interval_time = time.time()
            i += seq_len
            batch_i += 1

        mx.nd.waitall()

        print('[Epoch %d] throughput %.2f samples/s' % (
            epoch, (args.batch_size * len(train_data)) / (time.time() - start_epoch_time)))

        if args.ntasgd and ntasgd:
            mx.nd.save('{}.val.params'.format(args.save), param_dict_avg)
        else:
            model.save_parameters('{}.val.params'.format(args.save))
        val_L = evaluate(val_data, val_batch_size, '{}.val.params'.format(args.save), context[0])
        print('[Epoch %d] time cost %.2fs, valid loss %.2f, valid ppl %.2f，lr %.2f' % (
            epoch, time.time() - start_epoch_time, val_L, math.exp(val_L),
            trainer.learning_rate))

        if args.ntasgd and avg_trigger == 0:
            if t > n and val_L > min(valid_losses[-n:]):
                if param_dict_avg is None:
                    param_dict_avg = {k.split(model._prefix)[1]: v.data(context[0]).copy()
                                      for k, v in parameters.items()}
                else:
                    for k, v in parameters.items():
                        param_dict_avg[k.split(model._prefix)[1]] \
                            = v.data(context[0]).copy()
                avg_trigger = epoch * (len(train_data) // args.bptt) + len(train_data) // args.bptt
                print('Switching to NTASGD and avg_trigger is : %d' % avg_trigger)
                ntasgd = True
            valid_losses.append(val_L)
            t += 1

        if val_L < best_val:
            update_lr_epoch = 0
            best_val = val_L
            if args.ntasgd and ntasgd:
                mx.nd.save(args.save, param_dict_avg)
            else:
                model.save_parameters(args.save)
            test_L = evaluate(test_data, test_batch_size, args.save, context[0])
            print('[Epoch %d] test loss %.2f, test ppl %.2f'
                  % (epoch, test_L, math.exp(test_L)))
        else:
            update_lr_epoch += 1
            if update_lr_epoch % args.lr_update_interval == 0 and update_lr_epoch != 0:
                lr_scale = trainer.learning_rate * args.lr_update_factor
                print('Learning rate after interval update %f' % lr_scale)
                trainer.set_learning_rate(lr_scale)
                update_lr_epoch = 0

    print('Total training throughput %.2f samples/s'
          % ((args.batch_size * len(train_data) * args.epochs) / (time.time() - start_train_time)))