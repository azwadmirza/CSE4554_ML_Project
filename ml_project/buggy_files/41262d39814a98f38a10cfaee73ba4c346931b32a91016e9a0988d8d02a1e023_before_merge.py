    def __init__(self, classifier, max_iter=1000, eta=0.01, batch_size=128):
        """
        Create a NewtonFool attack instance.

        :param classifier: A trained model.
        :type classifier: :class:`Classifier`
        :param max_iter: The maximum number of iterations.
        :type max_iter: `int`
        :param eta: The eta coefficient.
        :type eta: `float`
        :param batch_size: Batch size
        :type batch_size: `int`
        """
        super(NewtonFool, self).__init__(classifier)
        params = {"max_iter": max_iter, "eta": eta, "batch_size": batch_size}
        self.set_params(**params)