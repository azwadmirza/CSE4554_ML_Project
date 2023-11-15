    def __init__(self, classifier, max_iter=100, epsilon=1e-6):
        """
        Create a DeepFool attack instance.

        :param classifier: A trained model.
        :type classifier: :class:`Classifier`
        :param max_iter: The maximum number of iterations.
        :type max_iter: `int`
        :param epsilon: Overshoot parameter.
        :type epsilon: `float`
        """
        super(DeepFool, self).__init__(classifier)
        params = {'max_iter': max_iter, 'epsilon': epsilon}
        self.set_params(**params)