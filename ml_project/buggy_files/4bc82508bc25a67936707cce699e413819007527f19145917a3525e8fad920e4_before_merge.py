def create_training_dataset(
    config,
    num_shuffles=1,
    Shuffles=None,
    windows2linux=False,
    userfeedback=False,
    trainIndices=None,
    testIndices=None,
    net_type=None,
    augmenter_type=None,
):
    """
    Creates a training dataset. Labels from all the extracted frames are merged into a single .h5 file.\n
    Only the videos included in the config file are used to create this dataset.\n

    [OPTIONAL] Use the function 'add_new_video' at any stage of the project to add more videos to the project.

    Parameter
    ----------
    config : string
        Full path of the config.yaml file as a string.

    num_shuffles : int, optional
        Number of shuffles of training dataset to create, i.e. [1,2,3] for num_shuffles=3. Default is set to 1.

    Shuffles: list of shuffles.
        Alternatively the user can also give a list of shuffles (integers!).

    windows2linux: bool.
        The annotation files contain path formated according to your operating system. If you label on windows
        but train & evaluate on a unix system (e.g. ubunt, colab, Mac) set this variable to True to convert the paths.

    userfeedback: bool, optional
        If this is set to false, then all requested train/test splits are created (no matter if they already exist). If you
        want to assure that previous splits etc. are not overwritten, then set this to True and you will be asked for each split.

    trainIndices: list of lists, optional (default=None)
        List of one or multiple lists containing train indexes.
        A list containing two lists of training indexes will produce two splits.

    testIndices: list of lists, optional (default=None)
        List of one or multiple lists containing test indexes.

    net_type: list
        Type of networks. Currently resnet_50, resnet_101, resnet_152, mobilenet_v2_1.0, mobilenet_v2_0.75,
        mobilenet_v2_0.5, mobilenet_v2_0.35, efficientnet_b0, efficientnet_b1, efficientnet_b2, efficientnet_b3,
        efficientnet_b4, efficientnet_b5, and efficientnet_b6 are supported.

    augmenter_type: string
        Type of augmenter. Currently default, imgaug, tensorpack, and deterministic are supported.

    Example
    --------
    >>> deeplabcut.create_training_dataset('/analysis/project/reaching-task/config.yaml',num_shuffles=1)
    Windows:
    >>> deeplabcut.create_training_dataset('C:\\Users\\Ulf\\looming-task\\config.yaml',Shuffles=[3,17,5])
    --------
    """
    import scipy.io as sio

    # Loading metadata from config file:
    cfg = auxiliaryfunctions.read_config(config)
    if cfg.get("multianimalproject", False):
        from deeplabcut.generate_training_dataset.multiple_individuals_trainingsetmanipulation import (
            create_multianimaltraining_dataset,
        )

        create_multianimaltraining_dataset(
            config, num_shuffles, Shuffles, windows2linux, net_type
        )
    else:
        scorer = cfg["scorer"]
        project_path = cfg["project_path"]
        # Create path for training sets & store data there
        trainingsetfolder = auxiliaryfunctions.GetTrainingSetFolder(
            cfg
        )  # Path concatenation OS platform independent
        auxiliaryfunctions.attempttomakefolder(
            Path(os.path.join(project_path, str(trainingsetfolder))), recursive=True
        )

        Data = merge_annotateddatasets(
            cfg, Path(os.path.join(project_path, trainingsetfolder)), windows2linux
        )
        if Data is None:
            return
        Data = Data[scorer]  # extract labeled data

        # loading & linking pretrained models
        if net_type is None:  # loading & linking pretrained models
            net_type = cfg.get("default_net_type", "resnet_50")
        else:
            if "resnet" in net_type or "mobilenet" in net_type or "efficientnet" in net_type:
                pass
            else:
                raise ValueError("Invalid network type:", net_type)

        if augmenter_type is None:
            augmenter_type = cfg.get("default_augmenter", "imgaug")
            if augmenter_type is None:  # this could be in config.yaml for old projects!
                # updating variable if null/None! #backwardscompatability
                auxiliaryfunctions.edit_config(config, {"default_augmenter": "imgaug"})
                augmenter_type = "imgaug"
        else:
            if augmenter_type in [
                "default",
                "scalecrop",
                "imgaug",
                "tensorpack",
                "deterministic",
            ]:
                pass
            else:
                raise ValueError("Invalid augmenter type:", augmenter_type)

        # Loading the encoder (if necessary downloading from TF)
        dlcparent_path = auxiliaryfunctions.get_deeplabcut_path()
        defaultconfigfile = os.path.join(dlcparent_path, "pose_cfg.yaml")
        model_path, num_shuffles = auxfun_models.Check4weights(
            net_type, Path(dlcparent_path), num_shuffles
        )

        if Shuffles is None:
            Shuffles = range(1, num_shuffles + 1)
        else:
            Shuffles = [i for i in Shuffles if isinstance(i, int)]

        # print(trainIndices,testIndices, Shuffles, augmenter_type,net_type)
        if trainIndices is None and testIndices is None:
            splits = [
                (
                    trainFraction,
                    shuffle,
                    SplitTrials(range(len(Data.index)), trainFraction),
                )
                for trainFraction in cfg["TrainingFraction"]
                for shuffle in Shuffles
            ]
        else:
            if len(trainIndices) != len(testIndices) != len(Shuffles):
                raise ValueError(
                    "Number of Shuffles and train and test indexes should be equal."
                )
            splits = []
            for shuffle, (train_inds, test_inds) in enumerate(
                zip(trainIndices, testIndices)
            ):
                trainFraction = round(
                    len(train_inds) * 1.0 / (len(train_inds) + len(test_inds)), 2
                )
                print(
                    f"You passed a split with the following fraction: {int(100 * trainFraction)}%"
                )
                splits.append(
                    (trainFraction, Shuffles[shuffle], (train_inds, test_inds))
                )

        bodyparts = cfg["bodyparts"]
        nbodyparts = len(bodyparts)
        for trainFraction, shuffle, (trainIndices, testIndices) in splits:
            if len(trainIndices) > 0:
                if userfeedback:
                    trainposeconfigfile, _, _ = training.return_train_network_path(
                        config,
                        shuffle=shuffle,
                        trainingsetindex=cfg["TrainingFraction"].index(trainFraction),
                    )
                    if trainposeconfigfile.is_file():
                        askuser = input(
                            "The model folder is already present. If you continue, it will overwrite the existing model (split). Do you want to continue?(yes/no): "
                        )
                        if (
                            askuser == "no"
                            or askuser == "No"
                            or askuser == "N"
                            or askuser == "No"
                        ):
                            raise Exception(
                                "Use the Shuffles argument as a list to specify a different shuffle index. Check out the help for more details."
                            )

                ####################################################
                # Generating data structure with labeled information & frame metadata (for deep cut)
                ####################################################
                # Make training file!
                (
                    datafilename,
                    metadatafilename,
                ) = auxiliaryfunctions.GetDataandMetaDataFilenames(
                    trainingsetfolder, trainFraction, shuffle, cfg
                )

                ################################################################################
                # Saving data file (convert to training file for deeper cut (*.mat))
                ################################################################################
                data, MatlabData = format_training_data(
                    Data, trainIndices, nbodyparts, project_path
                )
                sio.savemat(
                    os.path.join(project_path, datafilename), {"dataset": MatlabData}
                )

                ################################################################################
                # Saving metadata (Pickle file)
                ################################################################################
                auxiliaryfunctions.SaveMetadata(
                    os.path.join(project_path, metadatafilename),
                    data,
                    trainIndices,
                    testIndices,
                    trainFraction,
                )

                ################################################################################
                # Creating file structure for training &
                # Test files as well as pose_yaml files (containing training and testing information)
                #################################################################################
                modelfoldername = auxiliaryfunctions.GetModelFolder(
                    trainFraction, shuffle, cfg
                )
                auxiliaryfunctions.attempttomakefolder(
                    Path(config).parents[0] / modelfoldername, recursive=True
                )
                auxiliaryfunctions.attempttomakefolder(
                    str(Path(config).parents[0] / modelfoldername) + "/train"
                )
                auxiliaryfunctions.attempttomakefolder(
                    str(Path(config).parents[0] / modelfoldername) + "/test"
                )

                path_train_config = str(
                    os.path.join(
                        cfg["project_path"],
                        Path(modelfoldername),
                        "train",
                        "pose_cfg.yaml",
                    )
                )
                path_test_config = str(
                    os.path.join(
                        cfg["project_path"],
                        Path(modelfoldername),
                        "test",
                        "pose_cfg.yaml",
                    )
                )
                # str(cfg['proj_path']+'/'+Path(modelfoldername) / 'test'  /  'pose_cfg.yaml')
                items2change = {
                    "dataset": datafilename,
                    "metadataset": metadatafilename,
                    "num_joints": len(bodyparts),
                    "all_joints": [[i] for i in range(len(bodyparts))],
                    "all_joints_names": [str(bpt) for bpt in bodyparts],
                    "init_weights": model_path,
                    "project_path": str(cfg["project_path"]),
                    "net_type": net_type,
                    "dataset_type": augmenter_type,
                }

                items2drop = {}
                if augmenter_type == "scalecrop":
                    # these values are dropped as scalecrop
                    # doesn't have rotation implemented
                    items2drop = {"rotation": 0, "rotratio": 0.0}

                trainingdata = MakeTrain_pose_yaml(
                    items2change, path_train_config, defaultconfigfile, items2drop
                )

                keys2save = [
                    "dataset",
                    "num_joints",
                    "all_joints",
                    "all_joints_names",
                    "net_type",
                    "init_weights",
                    "global_scale",
                    "location_refinement",
                    "locref_stdev",
                ]
                MakeTest_pose_yaml(trainingdata, keys2save, path_test_config)
                print(
                    "The training dataset is successfully created. Use the function 'train_network' to start training. Happy training!"
                )
        return splits