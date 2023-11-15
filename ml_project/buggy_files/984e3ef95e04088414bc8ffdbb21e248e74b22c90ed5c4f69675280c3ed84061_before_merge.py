def train_example(num_workers=1, use_gpu=False, test_mode=False):
    config = {
        "test_mode": test_mode,
        "batch_size": 16 if test_mode else 512 // num_workers,
        "classification_model_path": os.path.join(
            os.path.dirname(ray.__file__),
            "util/sgd/torch/examples/mnist_cnn.pt")
    }
    trainer = TorchTrainer(
        model_creator=model_creator,
        data_creator=data_creator,
        optimizer_creator=optimizer_creator,
        loss_creator=nn.BCELoss,
        training_operator_cls=GANOperator,
        num_workers=num_workers,
        config=config,
        use_gpu=use_gpu,
        use_tqdm=True)

    from tabulate import tabulate
    pbar = trange(5, unit="epoch")
    for itr in pbar:
        stats = trainer.train(info=dict(epoch_idx=itr, num_epochs=5))
        pbar.set_postfix(dict(loss_g=stats["loss_g"], loss_d=stats["loss_d"]))
        formatted = tabulate([stats], headers="keys")
        if itr > 0:  # Get the last line of the stats.
            formatted = formatted.split("\n")[-1]
        pbar.write(formatted)

    return trainer