def hpo_pipeline(
    *,
    # 1. Dataset
    dataset: Union[None, str, Dataset, Type[Dataset]] = None,
    dataset_kwargs: Optional[Mapping[str, Any]] = None,
    training: Union[None, str, TriplesFactory] = None,
    testing: Union[None, str, TriplesFactory] = None,
    validation: Union[None, str, TriplesFactory] = None,
    evaluation_entity_whitelist: Optional[Collection[str]] = None,
    evaluation_relation_whitelist: Optional[Collection[str]] = None,
    # 2. Model
    model: Union[str, Type[Model]],
    model_kwargs: Optional[Mapping[str, Any]] = None,
    model_kwargs_ranges: Optional[Mapping[str, Any]] = None,
    # 3. Loss
    loss: Union[None, str, Type[Loss]] = None,
    loss_kwargs: Optional[Mapping[str, Any]] = None,
    loss_kwargs_ranges: Optional[Mapping[str, Any]] = None,
    # 4. Regularizer
    regularizer: Union[None, str, Type[Regularizer]] = None,
    regularizer_kwargs: Optional[Mapping[str, Any]] = None,
    regularizer_kwargs_ranges: Optional[Mapping[str, Any]] = None,
    # 5. Optimizer
    optimizer: Union[None, str, Type[Optimizer]] = None,
    optimizer_kwargs: Optional[Mapping[str, Any]] = None,
    optimizer_kwargs_ranges: Optional[Mapping[str, Any]] = None,
    # 6. Training Loop
    training_loop: Union[None, str, Type[TrainingLoop]] = None,
    negative_sampler: Union[None, str, Type[NegativeSampler]] = None,
    negative_sampler_kwargs: Optional[Mapping[str, Any]] = None,
    negative_sampler_kwargs_ranges: Optional[Mapping[str, Any]] = None,
    # 7. Training
    training_kwargs: Optional[Mapping[str, Any]] = None,
    training_kwargs_ranges: Optional[Mapping[str, Any]] = None,
    stopper: Union[None, str, Type[Stopper]] = None,
    stopper_kwargs: Optional[Mapping[str, Any]] = None,
    # 8. Evaluation
    evaluator: Union[None, str, Type[Evaluator]] = None,
    evaluator_kwargs: Optional[Mapping[str, Any]] = None,
    evaluation_kwargs: Optional[Mapping[str, Any]] = None,
    metric: Optional[str] = None,
    # 9. Tracking
    result_tracker: Union[None, str, Type[ResultTracker]] = None,
    result_tracker_kwargs: Optional[Mapping[str, Any]] = None,
    # 6. Misc
    device: Union[None, str, torch.device] = None,
    #  Optuna Study Settings
    storage: Union[None, str, BaseStorage] = None,
    sampler: Union[None, str, Type[BaseSampler]] = None,
    sampler_kwargs: Optional[Mapping[str, Any]] = None,
    pruner: Union[None, str, Type[BasePruner]] = None,
    pruner_kwargs: Optional[Mapping[str, Any]] = None,
    study_name: Optional[str] = None,
    direction: Optional[str] = None,
    load_if_exists: bool = False,
    # Optuna Optimization Settings
    n_trials: Optional[int] = None,
    timeout: Optional[int] = None,
    n_jobs: Optional[int] = None,
    save_model_directory: Optional[str] = None,
) -> HpoPipelineResult:
    """Train a model on the given dataset.

    :param dataset:
        The name of the dataset (a key from :data:`pykeen.datasets.datasets`) or the :class:`pykeen.datasets.Dataset`
        instance. Alternatively, the training triples factory (``training``), testing triples factory (``testing``),
        and validation triples factory (``validation``; optional) can be specified.
    :param dataset_kwargs:
        The keyword arguments passed to the dataset upon instantiation
    :param training:
        A triples factory with training instances or path to the training file if a a dataset was not specified
    :param testing:
        A triples factory with test instances or path to the test file if a dataset was not specified
    :param validation:
        A triples factory with validation instances or path to the validation file if a dataset was not specified
    :param evaluation_entity_whitelist:
        Optional restriction of evaluation to triples containing *only* these entities. Useful if the downstream task
        is only interested in certain entities, but the relational patterns with other entities improve the entity
        embedding quality. Passed to :func:`pykeen.pipeline.pipeline`.
    :param evaluation_relation_whitelist:
        Optional restriction of evaluation to triples containing *only* these relations. Useful if the downstream task
        is only interested in certain relation, but the relational patterns with other relations improve the entity
        embedding quality. Passed to :func:`pykeen.pipeline.pipeline`.

    :param model:
        The name of the model or the model class to pass to :func:`pykeen.pipeline.pipeline`
    :param model_kwargs:
        Keyword arguments to pass to the model class on instantiation
    :param model_kwargs_ranges:
        Strategies for optimizing the models' hyper-parameters to override
        the defaults

    :param loss:
        The name of the loss or the loss class to pass to :func:`pykeen.pipeline.pipeline`
    :param loss_kwargs:
        Keyword arguments to pass to the loss on instantiation
    :param loss_kwargs_ranges:
        Strategies for optimizing the losses' hyper-parameters to override
        the defaults

    :param regularizer:
        The name of the regularizer or the regularizer class to pass to :func:`pykeen.pipeline.pipeline`
    :param regularizer_kwargs:
        Keyword arguments to pass to the regularizer on instantiation
    :param regularizer_kwargs_ranges:
        Strategies for optimizing the regularizers' hyper-parameters to override
        the defaults

    :param optimizer:
        The name of the optimizer or the optimizer class. Defaults to :class:`torch.optim.Adagrad`.
    :param optimizer_kwargs:
        Keyword arguments to pass to the optimizer on instantiation
    :param optimizer_kwargs_ranges:
        Strategies for optimizing the optimizers' hyper-parameters to override
        the defaults

    :param training_loop:
        The name of the training approach (``'slcwa'`` or ``'lcwa'``) or the training loop class
        to pass to :func:`pykeen.pipeline.pipeline`
    :param negative_sampler:
        The name of the negative sampler (``'basic'`` or ``'bernoulli'``) or the negative sampler class
        to pass to :func:`pykeen.pipeline.pipeline`. Only allowed when training with sLCWA.
    :param negative_sampler_kwargs:
        Keyword arguments to pass to the negative sampler class on instantiation
    :param negative_sampler_kwargs_ranges:
        Strategies for optimizing the negative samplers' hyper-parameters to override
        the defaults

    :param training_kwargs:
        Keyword arguments to pass to the training loop's train function on call
    :param training_kwargs_ranges:
        Strategies for optimizing the training loops' hyper-parameters to override
        the defaults. Can not specify ranges for batch size if early stopping is enabled.

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

    :param metric:
        The metric to optimize over. Defaults to ``adjusted_mean_rank``.
    :param direction:
        The direction of optimization. Because the default metric is ``adjusted_mean_rank``,
        the default direction is ``minimize``.

    :param n_jobs: The number of parallel jobs. If this argument is set to :obj:`-1`, the number is
                set to CPU counts. If none, defaults to 1.

    .. note::

        The remaining parameters are passed to :func:`optuna.study.create_study`
        or :meth:`optuna.study.Study.optimize`.
    """
    sampler_cls = get_sampler_cls(sampler)
    pruner_cls = get_pruner_cls(pruner)

    if direction is None:
        direction = 'minimize'

    study = create_study(
        storage=storage,
        sampler=sampler_cls(**(sampler_kwargs or {})),
        pruner=pruner_cls(**(pruner_kwargs or {})),
        study_name=study_name,
        direction=direction,
        load_if_exists=load_if_exists,
    )

    # 0. Metadata/Provenance
    study.set_user_attr('pykeen_version', get_version())
    study.set_user_attr('pykeen_git_hash', get_git_hash())
    # 1. Dataset
    study.set_user_attr('dataset', _get_dataset_name(
        dataset=dataset,
        dataset_kwargs=dataset_kwargs,
        training=training,
        testing=testing,
        validation=validation,
    ))

    # 2. Model
    model: Type[Model] = get_model_cls(model)
    study.set_user_attr('model', normalize_string(model.__name__))
    logger.info(f'Using model: {model}')
    # 3. Loss
    loss: Type[Loss] = model.loss_default if loss is None else get_loss_cls(loss)
    study.set_user_attr('loss', normalize_string(loss.__name__, suffix=_LOSS_SUFFIX))
    logger.info(f'Using loss: {loss}')
    # 4. Regularizer
    regularizer: Type[Regularizer] = (
        model.regularizer_default
        if regularizer is None else
        get_regularizer_cls(regularizer)
    )
    study.set_user_attr('regularizer', regularizer.get_normalized_name())
    logger.info(f'Using regularizer: {regularizer}')
    # 5. Optimizer
    optimizer: Type[Optimizer] = get_optimizer_cls(optimizer)
    study.set_user_attr('optimizer', normalize_string(optimizer.__name__))
    logger.info(f'Using optimizer: {optimizer}')
    # 6. Training Loop
    training_loop: Type[TrainingLoop] = get_training_loop_cls(training_loop)
    study.set_user_attr('training_loop', training_loop.get_normalized_name())
    logger.info(f'Using training loop: {training_loop}')
    if training_loop is SLCWATrainingLoop:
        negative_sampler: Optional[Type[NegativeSampler]] = get_negative_sampler_cls(negative_sampler)
        study.set_user_attr('negative_sampler', negative_sampler.get_normalized_name())
        logger.info(f'Using negative sampler: {negative_sampler}')
    else:
        negative_sampler: Optional[Type[NegativeSampler]] = None
    # 7. Training
    stopper: Type[Stopper] = get_stopper_cls(stopper)

    if stopper is EarlyStopper and training_kwargs_ranges and 'epochs' in training_kwargs_ranges:
        raise ValueError('can not use early stopping while optimizing epochs')

    # 8. Evaluation
    evaluator: Type[Evaluator] = get_evaluator_cls(evaluator)
    study.set_user_attr('evaluator', evaluator.get_normalized_name())
    logger.info(f'Using evaluator: {evaluator}')
    if metric is None:
        metric = 'adjusted_mean_rank'
    study.set_user_attr('metric', metric)
    logger.info(f'Attempting to {direction} {metric}')

    # 9. Tracking
    result_tracker: Type[ResultTracker] = get_result_tracker_cls(result_tracker)

    objective = Objective(
        # 1. Dataset
        dataset=dataset,
        dataset_kwargs=dataset_kwargs,
        training=training,
        testing=testing,
        validation=validation,
        evaluation_entity_whitelist=evaluation_entity_whitelist,
        evaluation_relation_whitelist=evaluation_relation_whitelist,
        # 2. Model
        model=model,
        model_kwargs=model_kwargs,
        model_kwargs_ranges=model_kwargs_ranges,
        # 3. Loss
        loss=loss,
        loss_kwargs=loss_kwargs,
        loss_kwargs_ranges=loss_kwargs_ranges,
        # 4. Regularizer
        regularizer=regularizer,
        regularizer_kwargs=regularizer_kwargs,
        regularizer_kwargs_ranges=regularizer_kwargs_ranges,
        # 5. Optimizer
        optimizer=optimizer,
        optimizer_kwargs=optimizer_kwargs,
        optimizer_kwargs_ranges=optimizer_kwargs_ranges,
        # 6. Training Loop
        training_loop=training_loop,
        negative_sampler=negative_sampler,
        negative_sampler_kwargs=negative_sampler_kwargs,
        negative_sampler_kwargs_ranges=negative_sampler_kwargs_ranges,
        # 7. Training
        training_kwargs=training_kwargs,
        training_kwargs_ranges=training_kwargs_ranges,
        stopper=stopper,
        stopper_kwargs=stopper_kwargs,
        # 8. Evaluation
        evaluator=evaluator,
        evaluator_kwargs=evaluator_kwargs,
        evaluation_kwargs=evaluation_kwargs,
        # 9. Tracker
        result_tracker=result_tracker,
        result_tracker_kwargs=result_tracker_kwargs,
        # Optuna Misc.
        metric=metric,
        save_model_directory=save_model_directory,
        # Pipeline Misc.
        device=device,
    )

    # Invoke optimization of the objective function.
    study.optimize(
        objective,
        n_trials=n_trials,
        timeout=timeout,
        n_jobs=n_jobs or 1,
    )

    return HpoPipelineResult(
        study=study,
        objective=objective,
    )