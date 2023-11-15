    def __init__(self, classifier, max_iter=100, epsilon=1e-6, nb_grads=10, batch_size=128, expectation=None):
        """
        Create a DeepFool attack instance.

        :param classifier: A trained model.
        :type classifier: :class:`Classifier`
        :param max_iter: The maximum number of iterations.
        :type max_iter: `int`
        :param epsilon: Overshoot parameter.
        :type epsilon: `float`
        :param nb_grads: The number of class gradients (top nb_grads w.r.t. prediction) to compute. This way only the
                         most likely classes are considered, speeding up the computation.
        :type nb_grads: `int`
        :param batch_size: Batch size
        :type batch_size: `int`
        :param expectation: An expectation over transformations to be applied when computing
                            classifier gradients and predictions.
        :type expectation: :class:`ExpectationOverTransformations`
        """
        super(DeepFool, self).__init__(classifier=classifier, expectation=expectation)
        params = {'max_iter': max_iter, 'epsilon': epsilon, 'nb_grads': nb_grads, 'batch_size': batch_size}
        self.set_params(**params)