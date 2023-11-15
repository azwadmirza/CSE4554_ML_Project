def main(args):
    # load and preprocess dataset
    data = load_data(args)

    features = mx.nd.array(data.features)
    labels = mx.nd.array(data.labels)
    mask = mx.nd.array(np.where(data.train_mask == 1))
    test_mask = mx.nd.array(np.where(data.test_mask == 1))
    val_mask = mx.nd.array(np.where(data.val_mask == 1))
    in_feats = features.shape[1]
    n_classes = data.num_labels
    n_edges = data.graph.number_of_edges()

    if args.gpu < 0:
        ctx = mx.cpu()
    else:
        ctx = mx.gpu(args.gpu)
        features = features.as_in_context(ctx)
        labels = labels.as_in_context(ctx)
        mask = mask.as_in_context(ctx)
        test_mask = test_mask.as_in_context(ctx)
        val_mask = val_mask.as_in_context(ctx)
    # create graph
    g = data.graph
    # add self-loop
    g.remove_edges_from(nx.selfloop_edges(g))
    g = DGLGraph(g)
    g.add_edges(g.nodes(), g.nodes())
    # create model
    heads = ([args.num_heads] * args.num_layers) + [args.num_out_heads]
    model = GAT(g,
                args.num_layers,
                in_feats,
                args.num_hidden,
                n_classes,
                heads,
                elu,
                args.in_drop,
                args.attn_drop,
                args.alpha,
                args.residual)

    stopper = EarlyStopping(patience=100)
    model.initialize(ctx=ctx)

    # use optimizer
    trainer = gluon.Trainer(model.collect_params(), 'adam', {'learning_rate': args.lr})

    dur = []
    for epoch in range(args.epochs):
        if epoch >= 3:
            t0 = time.time()
        # forward
        with mx.autograd.record():
            logits = model(features)
            loss = mx.nd.softmax_cross_entropy(logits[mask].squeeze(), labels[mask].squeeze())
            loss.backward()
        trainer.step(mask.shape[0])

        if epoch >= 3:
            dur.append(time.time() - t0)
        print("Epoch {:05d} | Loss {:.4f} | Time(s) {:.4f} | ETputs(KTEPS) {:.2f}".format(
            epoch, loss.asnumpy()[0], np.mean(dur), n_edges / np.mean(dur) / 1000))
        val_accuracy = evaluate(model, features, labels, val_mask)
        print("Validation Accuracy {:.4f}".format(val_accuracy))
        if stopper.step(val_accuracy, model): 
            break
    model.load_parameters('model.param')
    test_accuracy = evaluate(model, features, labels, test_mask)
    print("Test Accuracy {:.4f}".format(test_accuracy))