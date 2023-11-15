    def __init__(self, classifier, confidence=0.0, targeted=True, learning_rate=0.01,
                 max_iter=10, max_halving=5, max_doubling=5, eps=0.3, batch_size=128, expectation=None):
        """
        Create a Carlini L_Inf attack instance.

        :param classifier: A trained model.
        :type classifier: :class:`Classifier`
        :param confidence: Confidence of adversarial examples: a higher value produces examples that are farther away,
                from the original input, but classified with higher confidence as the target class.
        :type confidence: `float`
        :param targeted: Should the attack target one specific class.
        :type targeted: `bool`
        :param learning_rate: The initial learning rate for the attack algorithm. Smaller values produce better
                results but are slower to converge.
        :type learning_rate: `float`
        :param max_iter: The maximum number of iterations.
        :type max_iter: `int`
        :param max_halving: Maximum number of halving steps in the line search optimization.
        :type max_halving: `int`
        :param max_doubling: Maximum number of doubling steps in the line search optimization.
        :type max_doubling: `int`
        :param eps: An upper bound for the L_0 norm of the adversarial perturbation.
        :type eps: `float`
        :param batch_size: Internal size of batches on which adversarial samples are generated.
        :type batch_size: `int`
        :param expectation: An expectation over transformations to be applied when computing
                            classifier gradients and predictions.
        :type expectation: :class:`ExpectationOverTransformations`
        """
        super(CarliniLInfMethod, self).__init__(classifier)

        kwargs = {'confidence': confidence,
                  'targeted': targeted,
                  'learning_rate': learning_rate,
                  'max_iter': max_iter,
                  'max_halving': max_halving,
                  'max_doubling': max_doubling,
                  'eps': eps,
                  'batch_size': batch_size,
                  'expectation': expectation
                  }
        assert self.set_params(**kwargs)

        # There is one internal hyperparameter:
        # Smooth arguments of arctanh by multiplying with this constant to avoid division by zero:
        self._tanh_smoother = 0.999999