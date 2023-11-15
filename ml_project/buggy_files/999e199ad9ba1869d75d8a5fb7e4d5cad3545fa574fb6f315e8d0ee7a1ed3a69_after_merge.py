    def _update_confusion_matrix(self, y_true, y_pred, sample_weight):
        y_true = self._safe_squeeze(y_true)
        y_pred = self._safe_squeeze(y_pred)

        new_conf_mtx = tf.math.confusion_matrix(
            labels=y_true,
            predictions=y_pred,
            num_classes=self.num_classes,
            weights=sample_weight,
            dtype=tf.float32,
        )

        return self.conf_mtx.assign_add(new_conf_mtx)