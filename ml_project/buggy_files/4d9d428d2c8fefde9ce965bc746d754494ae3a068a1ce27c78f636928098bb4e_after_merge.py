    def __init__(self, classifier, attacker='deepfool', attacker_params=None, delta=0.2, max_iter=20, eps=10.0,
                 norm=np.inf, expectation=None):
        """
        :param classifier: A trained model.
        :type classifier: :class:`Classifier`
        :param attacker: Adversarial attack name. Default is 'deepfool'. Supported names: 'carlini', 'carlini_inf',
                         'deepfool', 'fgsm', 'bim', 'pgd', 'margin', 'ead', 'newtonfool', 'jsma', 'vat'.
        :type attacker: `str`
        :param attacker_params: Parameters specific to the adversarial attack.
        :type attacker_params: `dict`
        :param delta: desired accuracy
        :type delta: `float`
        :param max_iter: The maximum number of iterations for computing universal perturbation.
        :type max_iter: `int`
        :param eps: Attack step size (input variation)
        :type eps: `float`
        :param norm: Order of the norm. Possible values: np.inf, 2 (default is np.inf)
        :type norm: `int`
        :param expectation: An expectation over transformations to be applied when computing
                            classifier gradients and predictions.
        :type expectation: :class:`ExpectationOverTransformations`
        """
        super(UniversalPerturbation, self).__init__(classifier)
        kwargs = {'attacker': attacker,
                  'attacker_params': attacker_params,
                  'delta': delta,
                  'max_iter': max_iter,
                  'eps': eps,
                  'norm': norm,
                  'expectation': expectation
                  }
        self.set_params(**kwargs)