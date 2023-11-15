    def _binary_roc_auc_score(y_true, y_score, sample_weight=None):
        if len(np.unique(y_true)) != 2:
            raise ValueError("ROC AUC score is not defined")

        fpr, tpr, tresholds = roc_curve(y_true, y_score,
                                        sample_weight=sample_weight)
        return auc(fpr, tpr, reorder=True)