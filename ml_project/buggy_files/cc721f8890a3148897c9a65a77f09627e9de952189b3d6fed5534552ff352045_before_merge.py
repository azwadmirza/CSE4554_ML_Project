    def update_leaves_values(self, grower, y_true, raw_predictions,
                             sample_weight):
        # Update the values predicted by the tree with
        # median(y_true - raw_predictions).
        # See note about need_update_leaves_values in BaseLoss.

        # TODO: ideally this should be computed in parallel over the leaves
        # using something similar to _update_raw_predictions(), but this
        # requires a cython version of median()
        for leaf in grower.finalized_leaves:
            indices = leaf.sample_indices
            if sample_weight is None:
                median_res = np.median(y_true[indices]
                                       - raw_predictions[indices])
            else:
                median_res = _weighted_percentile(y_true[indices]
                                                  - raw_predictions[indices],
                                                  sample_weight=sample_weight,
                                                  percentile=50)
            leaf.value = grower.shrinkage * median_res