def pipeline(  # noqa: C901
    *,
    # 1. Dataset
    dataset: Union[None, str, Type[DataSet]] = None,
    dataset_kwargs: Optional[Mapping[str, Any]] = None,
    training_triples_factory: Optional[TriplesFactory] = None,
    testing_triples_factory: Optional[TriplesFactory] = None,
    validation_triples_factory: Optional[TriplesFactory] = None,
    evaluation_entity_whitelist: Optional[Collection[str]] = None,
    evaluation_relation_whitelist: Optional[Collection[str]] = None,
    # 2. Model
    model: Union[str, Type[Model]],
    model_kwargs: Optional[Mapping[str, Any]] = None,
    # 3. Loss
    loss: Union[None, str, Type[Loss]] = None,
    loss_kwargs: Optional[Mapping[str, Any]] = None,
    # 4. Regularizer
    regularizer: Union[None, str, Type[Regularizer]] = None,
    regularizer_kwargs: Optional[Mapping[str, Any]] = None,
    # 5. Optimizer
    optimizer: Union[None, str, Type[Optimizer]] = None,
    optimizer_kwargs: Optional[Mapping[str, Any]] = None,
    clear_optimizer: bool = True,
    # 6. Training Loop
    training_loop: Union[None, str, Type[TrainingLoop]] = None,
    negative_sampler: Union[None, str, Type[NegativeSampler]] = None,
    negative_sampler_kwargs: Optional[Mapping[str, Any]] = None,
    # 7. Training (ronaldo style)
    training_kwargs: Optional[Mapping[str, Any]] = None,
    stopper: Union[None, str, Type[Stopper]] = None,
    stopper_kwargs: Optional[Mapping[str, Any]] = None,
    # 8. Evaluation
    evaluator: Union[None, str, Type[Evaluator]] = None,
    evaluator_kwargs: Optional[Mapping[str, Any]] = None,
    evaluation_kwargs: Optional[Mapping[str, Any]] = None,
    # 9. Tracking
    result_tracker: Union[None, str, Type[ResultTracker]] = None,
    result_tracker_kwargs: Optional[Mapping[str, Any]] = None,
    # Misc
    metadata: Optional[Dict[str, Any]] = None,
    device: Union[None, str, torch.device] = None,
    random_seed: Optional[int] = None,
    use_testing_data: bool = True,
) -> PipelineResult:
    """Train and evaluate a model.

    :param dataset:
        The name of the dataset (a key from :data:`pykeen.datasets.datasets`) or the :class:`pykeen.datasets.DataSet`
        instance. Alternatively, the ``training_triples_factory`` and ``testing_triples_factory`` can be specified.
    :param dataset_kwargs:
        The keyword arguments passed to the dataset upon instantiation
    :param training_triples_factory:
        A triples factory with training instances if a dataset was not specified
    :param testing_triples_factory:
        A triples factory with training instances if a dataset was not specified
    :param validation_triples_factory:
        A triples factory with validation instances if a dataset was not specified
    :param evaluation_entity_whitelist:
        Optional restriction of evaluation to triples containing *only* these entities. Useful if the downstream task
        is only interested in certain entities, but the relational patterns with other entities improve the entity
        embedding quality.
    :param evaluation_relation_whitelist:
        Optional restriction of evaluation to triples containing *only* these relations. Useful if the downstream task
        is only interested in certain relation, but the relational patterns with other relations improve the entity
        embedding quality.

    :param model:
        The name of the model or the model class
    :param model_kwargs:
        Keyword arguments to pass to the model class on instantiation

    :param loss:
        The name of the loss or the loss class.
    :param loss_kwargs:
        Keyword arguments to pass to the loss on instantiation

    :param regularizer:
        The name of the regularizer or the regularizer class.
    :param regularizer_kwargs:
        Keyword arguments to pass to the regularizer on instantiation

    :param optimizer:
        The name of the optimizer or the optimizer class. Defaults to :class:`torch.optim.Adagrad`.
    :param optimizer_kwargs:
        Keyword arguments to pass to the optimizer on instantiation
    :param clear_optimizer:
        Whether to delete the optimizer instance after training. As the optimizer might have additional memory
        consumption due to e.g. moments in Adam, this is the default option. If you want to continue training, you
        should set it to False, as the optimizer's internal parameter will get lost otherwise.

    :param training_loop:
        The name of the training loop's training approach (``'slcwa'`` or ``'lcwa'``) or the training loop class.
        Defaults to :class:`pykeen.training.SLCWATrainingLoop`.
    :param negative_sampler:
        The name of the negative sampler (``'basic'`` or ``'bernoulli'``) or the negative sampler class.
        Only allowed when training with sLCWA.
        Defaults to :class:`pykeen.sampling.BasicNegativeSampler`.
    :param negative_sampler_kwargs:
        Keyword arguments to pass to the negative sampler class on instantiation

    :param training_kwargs:
        Keyword arguments to pass to the training loop's train function on call
    :param stopper:
        What kind of stopping to use. Default to no stopping, can be set to 'early'.
    :param stopper_kwargs:
        Keyword arguments to pass to the stopper upon instantiation.

    :param evaluator:
        The name of the evaluator or an evaluator class. Defaults to :class:`pykeen.evaluation.RankBasedEvaluator`.
    :param evaluator_kwargs:
        Keyword arguments to pass to the evaluator on instantiation
    :param evaluation_kwargs:
        Keyword arguments to pass to the evaluator's evaluate function on call

    :param result_tracker:
        The ResultsTracker class or name
    :param result_tracker_kwargs:
        The keyword arguments passed to the results tracker on instantiation

    :param metadata:
        A JSON dictionary to store with the experiment
    :param use_testing_data:
        If true, use the testing triples. Otherwise, use the validation triples. Defaults to true - use testing triples.
    """
    if random_seed is None:
        random_seed = random_non_negative_int()
        logger.warning(f'No random seed is specified. Setting to {random_seed}.')
    set_random_seed(random_seed)

    result_tracker_cls: Type[ResultTracker] = get_result_tracker_cls(result_tracker)
    result_tracker = result_tracker_cls(**(result_tracker_kwargs or {}))

    if not metadata:
        metadata = {}
    title = metadata.get('title')

    # Start tracking
    result_tracker.start_run(run_name=title)

    device = resolve_device(device)

    result_tracker.log_params(dict(dataset=dataset))

    training_triples_factory, testing_triples_factory, validation_triples_factory = get_dataset(
        dataset=dataset,
        dataset_kwargs=dataset_kwargs,
        training_triples_factory=training_triples_factory,
        testing_triples_factory=testing_triples_factory,
        validation_triples_factory=validation_triples_factory,
    )

    # evaluation restriction to a subset of entities/relations
    if any(f is not None for f in (evaluation_entity_whitelist, evaluation_relation_whitelist)):
        testing_triples_factory = testing_triples_factory.new_with_restriction(
            entities=evaluation_entity_whitelist,
            relations=evaluation_relation_whitelist,
        )
        if validation_triples_factory is not None:
            validation_triples_factory = validation_triples_factory.new_with_restriction(
                entities=evaluation_entity_whitelist,
                relations=evaluation_relation_whitelist,
            )

    if model_kwargs is None:
        model_kwargs = {}
    model_kwargs.update(preferred_device=device)
    model_kwargs.setdefault('random_seed', random_seed)

    if regularizer is not None:
        # FIXME this should never happen.
        if 'regularizer' in model_kwargs:
            logger.warning('Can not specify regularizer in kwargs and model_kwargs. removing from model_kwargs')
            del model_kwargs['regularizer']
        regularizer_cls: Type[Regularizer] = get_regularizer_cls(regularizer)
        model_kwargs['regularizer'] = regularizer_cls(
            device=device,
            **(regularizer_kwargs or {}),
        )

    if loss is not None:
        if 'loss' in model_kwargs:  # FIXME
            logger.warning('duplicate loss in kwargs and model_kwargs. removing from model_kwargs')
            del model_kwargs['loss']
        loss_cls = get_loss_cls(loss)
        _loss = loss_cls(**(loss_kwargs or {}))
        model_kwargs.setdefault('loss', _loss)

    model = get_model_cls(model)
    model_instance: Model = model(
        triples_factory=training_triples_factory,
        **model_kwargs,
    )
    # Log model parameters
    result_tracker.log_params(params=dict(cls=model.__name__, kwargs=model_kwargs), prefix='model')

    optimizer = get_optimizer_cls(optimizer)
    training_loop = get_training_loop_cls(training_loop)

    if optimizer_kwargs is None:
        optimizer_kwargs = {}

    # Log optimizer parameters
    result_tracker.log_params(params=dict(cls=optimizer.__name__, kwargs=optimizer_kwargs), prefix='optimizer')
    optimizer_instance = optimizer(
        params=model_instance.get_grad_params(),
        **optimizer_kwargs,
    )

    result_tracker.log_params(params=dict(cls=training_loop.__name__), prefix='training_loop')
    if negative_sampler is None:
        training_loop_instance: TrainingLoop = training_loop(
            model=model_instance,
            optimizer=optimizer_instance,
        )
    elif training_loop is not SLCWATrainingLoop:
        raise ValueError('Can not specify negative sampler with LCWA')
    else:
        negative_sampler = get_negative_sampler_cls(negative_sampler)
        result_tracker.log_params(
            params=dict(cls=negative_sampler.__name__, kwargs=negative_sampler_kwargs),
            prefix='negative_sampler',
        )
        training_loop_instance: TrainingLoop = SLCWATrainingLoop(
            model=model_instance,
            optimizer=optimizer_instance,
            negative_sampler_cls=negative_sampler,
            negative_sampler_kwargs=negative_sampler_kwargs,
        )

    evaluator = get_evaluator_cls(evaluator)
    evaluator_instance: Evaluator = evaluator(
        **(evaluator_kwargs or {}),
    )

    if evaluation_kwargs is None:
        evaluation_kwargs = {}

    if training_kwargs is None:
        training_kwargs = {}

    # Stopping
    if 'stopper' in training_kwargs and stopper is not None:
        raise ValueError('Specified stopper in training_kwargs and as stopper')
    if 'stopper' in training_kwargs:
        stopper = training_kwargs.pop('stopper')
    if stopper_kwargs is None:
        stopper_kwargs = {}

    # Load the evaluation batch size for the stopper, if it has been set
    _evaluation_batch_size = evaluation_kwargs.get('batch_size')
    if _evaluation_batch_size is not None:
        stopper_kwargs.setdefault('evaluation_batch_size', _evaluation_batch_size)

    # By default there's a stopper that does nothing interesting
    stopper_cls: Type[Stopper] = get_stopper_cls(stopper)
    stopper: Stopper = stopper_cls(
        model=model_instance,
        evaluator=evaluator_instance,
        evaluation_triples_factory=validation_triples_factory,
        result_tracker=result_tracker,
        **stopper_kwargs,
    )

    training_kwargs.setdefault('num_epochs', 5)
    training_kwargs.setdefault('batch_size', 256)
    result_tracker.log_params(params=training_kwargs, prefix='training')

    # Add logging for debugging
    logging.debug("Run Pipeline based on following config:")
    logging.debug(f"dataset: {dataset}")
    logging.debug(f"dataset_kwargs: {dataset_kwargs}")
    logging.debug(f"model: {model}")
    logging.debug(f"model_kwargs: {model_kwargs}")
    logging.debug(f"loss: {loss}")
    logging.debug(f"loss_kwargs: {loss_kwargs}")
    logging.debug(f"regularizer: {regularizer}")
    logging.debug(f"regularizer_kwargs: {regularizer_kwargs}")
    logging.debug(f"optimizer: {optimizer}")
    logging.debug(f"optimizer_kwargs: {optimizer_kwargs}")
    logging.debug(f"training_loop: {training_loop}")
    logging.debug(f"negative_sampler: {negative_sampler}")
    logging.debug(f"_negative_sampler_kwargs: {negative_sampler_kwargs}")
    logging.debug(f"_training_kwargs: {training_kwargs}")
    logging.debug(f"stopper: {stopper}")
    logging.debug(f"stopper_kwargs: {stopper_kwargs}")
    logging.debug(f"evaluator: {evaluator}")
    logging.debug(f"evaluator_kwargs: {evaluator_kwargs}")

    # Train like Cristiano Ronaldo
    training_start_time = time.time()
    losses = training_loop_instance.train(
        stopper=stopper,
        result_tracker=result_tracker,
        clear_optimizer=clear_optimizer,
        **training_kwargs,
    )
    training_end_time = time.time() - training_start_time

    if use_testing_data:
        mapped_triples = testing_triples_factory.mapped_triples
    else:
        mapped_triples = validation_triples_factory.mapped_triples

    # Evaluate
    # Reuse optimal evaluation parameters from training if available
    if evaluator_instance.batch_size is not None or evaluator_instance.slice_size is not None:
        evaluation_kwargs['batch_size'] = evaluator_instance.batch_size
        evaluation_kwargs['slice_size'] = evaluator_instance.slice_size
    # Add logging about evaluator for debugging
    logging.debug("Evaluation will be run with following parameters:")
    logging.debug(f"evaluation_kwargs: {evaluation_kwargs}")
    evaluate_start_time = time.time()
    metric_results: MetricResults = evaluator_instance.evaluate(
        model=model_instance,
        mapped_triples=mapped_triples,
        **evaluation_kwargs,
    )
    evaluate_end_time = time.time() - evaluate_start_time
    result_tracker.log_metrics(
        metrics=metric_results.to_dict(),
        step=training_kwargs.get('num_epochs'),
    )
    result_tracker.end_run()

    return PipelineResult(
        random_seed=random_seed,
        model=model_instance,
        training_loop=training_loop_instance,
        losses=losses,
        stopper=stopper,
        metric_results=metric_results,
        metadata=metadata,
        train_seconds=training_end_time,
        evaluate_seconds=evaluate_end_time,
    )