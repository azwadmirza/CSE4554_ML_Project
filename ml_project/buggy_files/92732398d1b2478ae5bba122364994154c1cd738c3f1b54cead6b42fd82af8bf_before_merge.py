    def predict(self, x, batch_size=128, **kwargs):
        """
        Perform prediction for a batch of inputs. Predictions from classifiers should only be aggregated if they all
        have the same type of output (e.g., probabilities). Otherwise, use `raw=True` to get predictions from all
        models without aggregation. The same option should be used for logits output, as logits are not comparable
        between models and should not be aggregated.

        :param x: Test set.
        :type x: `np.ndarray`
        :param raw: Return the individual classifier raw outputs (not aggregated).
        :type raw: `bool`
        :return: Array of predictions of shape `(nb_inputs, nb_classes)`, or of shape
                 `(nb_classifiers, nb_inputs, nb_classes)` if `raw=True`.
        :rtype: `np.ndarray`
        """
        if 'raw' in kwargs:
            raw = kwargs['raw']
        else:
            raise ValueError('Missing argument `raw`.')

        preds = np.array([self._classifier_weights[i] * self._classifiers[i].predict(x)
                          for i in range(self._nb_classifiers)])
        if raw:
            return preds

        # Aggregate predictions only at probabilities level, as logits are not comparable between models
        var_z = np.sum(preds, axis=0)
        return var_z