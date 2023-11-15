def create_training_model_comparison(
    config,
    trainindex=0,
    num_shuffles=1,
    net_types=["resnet_50"],
    augmenter_types=["default"],
    userfeedback=False,
    windows2linux=False,
):
    """
    Creates a training dataset with different networks and augmentation types (dataset_loader) so that the shuffles
    have same training and testing indices.

    Therefore, this function is useful for benchmarking the performance of different network and augmentation types on the same training/testdata.\n

    Parameter
    ----------
    config : string
        Full path of the config.yaml file as a string.

    trainindex: int, optional
        Either (in case uniform = True) indexes which element of TrainingFraction in the config file should be used (note it is a list!).
        Alternatively (uniform = False) indexes which folder is dropped, i.e. the first if trainindex=0, the second if trainindex =1, etc.

    num_shuffles : int, optional
        Number of shuffles of training dataset to create, i.e. [1,2,3] for num_shuffles=3. Default is set to 1.

    net_types: list
        Type of networks. Currently resnet_50, resnet_101, resnet_152, mobilenet_v2_1.0,mobilenet_v2_0.75, mobilenet_v2_0.5, mobilenet_v2_0.35,
        efficientnet_b0, efficientnet_b1, efficientnet_b2, efficientnet_b3, efficientnet_b4,
        efficientnet_b5, and efficientnet_b6 are supported.

    augmenter_types: list
        Type of augmenters. Currently "default", "imgaug", "tensorpack", and "deterministic" are supported.

    userfeedback: bool, optional
        If this is set to false, then all requested train/test splits are created (no matter if they already exist). If you
        want to assure that previous splits etc. are not overwritten, then set this to True and you will be asked for each split.

    windows2linux: bool.
        The annotation files contain path formated according to your operating system. If you label on windows
        but train & evaluate on a unix system (e.g. ubunt, colab, Mac) set this variable to True to convert the paths.

    Example
    --------
    >>> deeplabcut.create_training_model_comparison('/analysis/project/reaching-task/config.yaml',num_shuffles=1,net_types=['resnet_50','resnet_152'],augmenter_types=['tensorpack','deterministic'])

    Windows:
    >>> deeplabcut.create_training_model_comparison('C:\\Users\\Ulf\\looming-task\\config.yaml',num_shuffles=1,net_types=['resnet_50','resnet_152'],augmenter_types=['tensorpack','deterministic'])

    --------
    """
    # read cfg file
    cfg = auxiliaryfunctions.read_config(config)

    # create log file
    log_file_name = os.path.join(cfg["project_path"], "training_model_comparison.log")
    logger = logging.getLogger("training_model_comparison")
    if not logger.handlers:
        logger = logging.getLogger("training_model_comparison")
        hdlr = logging.FileHandler(log_file_name)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.INFO)
    else:
        pass

    largestshuffleindex = get_largestshuffle_index(config)

    for shuffle in range(num_shuffles):
        trainIndices, testIndices = mergeandsplit(
            config, trainindex=trainindex, uniform=True
        )
        for idx_net, net in enumerate(net_types):
            for idx_aug, aug in enumerate(augmenter_types):
                get_max_shuffle_idx = (
                    largestshuffleindex
                    + idx_aug
                    + idx_net * len(augmenter_types)
                    + shuffle * len(augmenter_types) * len(net_types)
                )
                log_info = str(
                    "Shuffle index:"
                    + str(get_max_shuffle_idx)
                    + ", net_type:"
                    + net
                    + ", augmenter_type:"
                    + aug
                    + ", trainsetindex:"
                    + str(trainindex)
                )
                create_training_dataset(
                    config,
                    Shuffles=[get_max_shuffle_idx],
                    net_type=net,
                    trainIndices=[trainIndices],
                    testIndices=[testIndices],
                    augmenter_type=aug,
                    userfeedback=userfeedback,
                    windows2linux=windows2linux,
                )
                logger.info(log_info)