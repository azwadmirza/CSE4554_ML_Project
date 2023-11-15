    def __init__(self, classifier, expectation=None):
        """
        :param classifier: A trained model.
        :type classifier: :class:`Classifier`
        :param expectation: An expectation over transformations to be applied when computing
                            classifier gradients and predictions.
        :type expectation: :class:`ExpectationOverTransformations`
        """
        self.classifier = classifier
        self.expectation = expectation