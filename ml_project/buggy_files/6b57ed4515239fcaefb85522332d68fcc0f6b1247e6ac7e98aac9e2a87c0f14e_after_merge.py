def fetch_lfw_pairs(subset='train', data_home=None, funneled=True, resize=0.5,
                    color=False, slice_=(slice(70, 195), slice(78, 172)),
                    download_if_missing=True):
    """Loader for the Labeled Faces in the Wild (LFW) pairs dataset

    This dataset is a collection of JPEG pictures of famous people
    collected on the internet, all details are available on the
    official website:

        http://vis-www.cs.umass.edu/lfw/

    Each picture is centered on a single face. Each pixel of each channel
    (color in RGB) is encoded by a float in range 0.0 - 1.0.

    The task is called Face Verification: given a pair of two pictures,
    a binary classifier must predict whether the two images are from
    the same person.

    In the official `README.txt`_ this task is described as the
    "Restricted" task.  As I am not sure as to implement the
    "Unrestricted" variant correctly, I left it as unsupported for now.

      .. _`README.txt`: http://vis-www.cs.umass.edu/lfw/README.txt

    The original images are 250 x 250 pixels, but the default slice and resize
    arguments reduce them to 62 x 74.

    Parameters
    ----------
    subset : optional, default: 'train'
        Select the dataset to load: 'train' for the development training
        set, 'test' for the development test set, and '10_folds' for the
        official evaluation set that is meant to be used with a 10-folds
        cross validation.

    data_home : optional, default: None
        Specify another download and cache folder for the datasets. By
        default all scikit learn data is stored in '~/scikit_learn_data'
        subfolders.

    funneled : boolean, optional, default: True
        Download and use the funneled variant of the dataset.

    resize : float, optional, default 0.5
        Ratio used to resize the each face picture.

    color : boolean, optional, default False
        Keep the 3 RGB channels instead of averaging them to a single
        gray level channel. If color is True the shape of the data has
        one more dimension than than the shape with color = False.

    slice_ : optional
        Provide a custom 2D slice (height, width) to extract the
        'interesting' part of the jpeg files and avoid use statistical
        correlation from the background

    download_if_missing : optional, True by default
        If False, raise a IOError if the data is not locally available
        instead of trying to download the data from the source site.

    Returns
    -------
    The data is returned as a Bunch object with the following attributes:

    data : numpy array of shape (2200, 5828)
        Each row corresponds to 2 ravel'd face images of original size 62 x 47
        pixels. Changing the ``slice_`` or resize parameters will change the shape
        of the output.

    pairs : numpy array of shape (2200, 2, 62, 47)
        Each row has 2 face images corresponding to same or different person
        from the dataset containing 5749 people. Changing the ``slice_`` or resize
        parameters will change the shape of the output.

    target : numpy array of shape (13233,)
        Labels associated to each pair of images. The two label values being
        different persons or the same person.

    DESCR : string
        Description of the Labeled Faces in the Wild (LFW) dataset.

    """
    lfw_home, data_folder_path = check_fetch_lfw(
        data_home=data_home, funneled=funneled,
        download_if_missing=download_if_missing)
    logger.info('Loading %s LFW pairs from %s', subset, lfw_home)

    # wrap the loader in a memoizing function that will return memmaped data
    # arrays for optimal memory usage
    m = Memory(cachedir=lfw_home, compress=6, verbose=0)
    load_func = m.cache(_fetch_lfw_pairs)

    # select the right metadata file according to the requested subset
    label_filenames = {
        'train': 'pairsDevTrain.txt',
        'test': 'pairsDevTest.txt',
        '10_folds': 'pairs.txt',
    }
    if subset not in label_filenames:
        raise ValueError("subset='%s' is invalid: should be one of %r" % (
            subset, list(sorted(label_filenames.keys()))))
    index_file_path = join(lfw_home, label_filenames[subset])

    # load and memoize the pairs as np arrays
    pairs, target, target_names = load_func(
        index_file_path, data_folder_path, resize=resize, color=color,
        slice_=slice_)

    # pack the results as a Bunch instance
    return Bunch(data=pairs.reshape(len(pairs), -1), pairs=pairs,
                 target=target, target_names=target_names,
                 DESCR="'%s' segment of the LFW pairs dataset" % subset)