    def __init__(self, classifier, max_iter=1, finite_diff=1e-6, eps=.1, batch_size=128, expectation=None):
        """
        Create a VirtualAdversarialMethod instance.

        :param classifier: A trained model.
        :type classifier: :class:`Classifier`
        :param eps: Attack step (max input variation).
        :type eps: `float`
        :param finite_diff: The finite difference parameter.
        :type finite_diff: `float`
        :param max_iter: The maximum number of iterations.
        :type max_iter: `int`
        :param batch_size: Batch size
        :type batch_size: `int`
        :param expectation: An expectation over transformations to be applied when computing
                            classifier gradients and predictions.
        :type expectation: :class:`ExpectationOverTransformations`
        """
        super(VirtualAdversarialMethod, self).__init__(classifier)
        kwargs = {'finite_diff': finite_diff,
                  'eps': eps,
                  'max_iter': max_iter,
                  'batch_size': batch_size,
                  'expectation': expectation}
        self.set_params(**kwargs)