def orpca(X, rank, fast=False,
          lambda1=None,
          lambda2=None,
          method=None,
          learning_rate=None,
          init=None,
          training_samples=None,
          momentum=None):
    """
    This function performs Online Robust PCA
    with missing or corrupted data.

    Parameters
    ----------
    X : {numpy array, iterator}
        [nfeatures x nsamples] matrix of observations
        or an iterator that yields samples, each with nfeatures elements.
    rank : int
        The model dimensionality.
    lambda1 : {None, float}
        Nuclear norm regularization parameter.
        If None, set to 1 / sqrt(nsamples)
    lambda2 : {None, float}
        Sparse error regularization parameter.
        If None, set to 1 / sqrt(nsamples)
    method : {None, 'CF', 'BCD', 'SGD', 'MomentumSGD'}
        'CF'  - Closed-form solver
        'BCD' - Block-coordinate descent
        'SGD' - Stochastic gradient descent
        'MomentumSGD' - Stochastic gradient descent with momentum
        If None, set to 'CF'
    learning_rate : {None, float}
        Learning rate for the stochastic gradient
        descent algorithm
        If None, set to 1
    init : {None, 'qr', 'rand', np.ndarray}
        'qr'   - QR-based initialization
        'rand' - Random initialization
        np.ndarray if the shape [nfeatures x rank].
        If None, set to 'qr'
    training_samples : {None, integer}
        Specifies the number of training samples to use in
        the 'qr' initialization
        If None, set to 10
    momentum : {None, float}
        Momentum parameter for 'MomentumSGD' method, should be
        a float between 0 and 1.
        If None, set to 0.5

    Returns
    -------
    Xhat : numpy array
        is the [nfeatures x nsamples] low-rank matrix
    Ehat : numpy array
        is the [nfeatures x nsamples] sparse error matrix
    U, S, V : numpy arrays
        are the results of an SVD on Xhat

    Notes
    -----
    The ORPCA code is based on a transcription of MATLAB code obtained from
    the following research paper:
       Jiashi Feng, Huan Xu and Shuicheng Yuan, "Online Robust PCA via
       Stochastic Optimization", Advances in Neural Information Processing
       Systems 26, (2013), pp. 404-412.

    It has been updated to include a new initialization method based
    on a QR decomposition of the first n "training" samples of the data.
    A stochastic gradient descent (SGD) solver is also implemented,
    along with a MomentumSGD solver for improved convergence and robustness
    with respect to local minima. More information about the gradient descent
    methods and choosing appropriate parameters can be found here:
       Sebastian Ruder, "An overview of gradient descent optimization
       algorithms", arXiv:1609.04747, (2016), http://arxiv.org/abs/1609.04747.

    """
    _orpca = ORPCA(rank, fast=fast, lambda1=lambda1,
                   lambda2=lambda2, method=method,
                   learning_rate=learning_rate, init=init,
                   training_samples=training_samples,
                   momentum=momentum)
    _orpca._setup(X, normalize=True)
    _orpca.fit(X)
    return _orpca.finish()