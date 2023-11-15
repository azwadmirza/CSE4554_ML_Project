    def __init__(self, classifier, theta=0.1, gamma=1.):
        """
        Create a SaliencyMapMethod instance.

        :param classifier: A trained model.
        :type classifier: :class:`Classifier`
        :param theta: Perturbation introduced to each modified feature per step (can be positive or negative).
        :type theta: `float`
        :param gamma: Maximum percentage of perturbed features (between 0 and 1).
        :type gamma: `float`
        """
        super(SaliencyMapMethod, self).__init__(classifier)
        kwargs = {
            'theta': theta,
            'gamma': gamma
            }
        self.set_params(**kwargs)