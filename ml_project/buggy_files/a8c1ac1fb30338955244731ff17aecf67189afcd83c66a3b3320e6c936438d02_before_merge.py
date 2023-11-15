    def _init_class_grads(self, label=None, logits=False):
        import keras.backend as k
        k.set_learning_phase(0)

        if len(self._output.shape) == 2:
            nb_outputs = self._output.shape[1]
        else:
            raise ValueError('Unexpected output shape for classification in Keras model.')

        if label is None:
            logger.debug('Computing class gradients for all %i classes.', self.nb_classes)
            if logits:
                if not hasattr(self, '_class_grads_logits'):
                    class_grads_logits = [k.gradients(self._preds_op[:, i], self._input)[0]
                                          for i in range(nb_outputs)]
                    self._class_grads_logits = k.function([self._input], class_grads_logits)
            else:
                if not hasattr(self, '_class_grads'):
                    class_grads = [k.gradients(k.softmax(self._preds_op)[:, i], self._input)[0]
                                   for i in range(nb_outputs)]
                    self._class_grads = k.function([self._input], class_grads)

        else:
            if isinstance(label, int):
                unique_labels = [label]
                logger.debug('Computing class gradients for class %i.', label)
            else:
                unique_labels = np.unique(label)
                logger.debug('Computing class gradients for classes %s.', str(unique_labels))

            if logits:
                if not hasattr(self, '_class_grads_logits_idx'):
                    self._class_grads_logits_idx = [None for _ in range(nb_outputs)]

                for l in unique_labels:
                    if self._class_grads_logits_idx[l] is None:
                        class_grads_logits = [k.gradients(self._preds_op[:, l], self._input)[0]]
                        self._class_grads_logits_idx[l] = k.function([self._input], class_grads_logits)
            else:
                if not hasattr(self, '_class_grads_idx'):
                    self._class_grads_idx = [None for _ in range(nb_outputs)]

                for l in unique_labels:
                    if self._class_grads_idx[l] is None:
                        class_grads = [k.gradients(k.softmax(self._preds_op)[:, l], self._input)[0]]
                        self._class_grads_idx[l] = k.function([self._input], class_grads)