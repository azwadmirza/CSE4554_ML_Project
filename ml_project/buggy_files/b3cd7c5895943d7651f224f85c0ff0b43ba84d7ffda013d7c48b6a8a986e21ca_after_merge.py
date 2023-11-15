    def __init__(self, classifier, theta=0.1, gamma=1., batch_size=128, expectation=None):
        """
        Create a SaliencyMapMethod instance.

        :param classifier: A trained model.
        :type classifier: :class:`Classifier`
        :param theta: Perturbation introduced to each modified feature per step (can be positive or negative).
        :type theta: `float`
        :param gamma: Maximum percentage of perturbed features (between 0 and 1).
        :type gamma: `float`
        :param batch_size: Batch size
        :type batch_size: `int`
        :param expectation: An expectation over transformations to be applied when computing
                            classifier gradients and predictions.
        :type expectation: :class:`ExpectationOverTransformations`
        """
        super(SaliencyMapMethod, self).__init__(classifier)
        kwargs = {'theta': theta, 'gamma': gamma, 'batch_size': batch_size, 'expectation': expectation}
        self.set_params(**kwargs)