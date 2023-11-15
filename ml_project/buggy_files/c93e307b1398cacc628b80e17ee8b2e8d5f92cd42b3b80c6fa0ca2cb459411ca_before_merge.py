    def get_attributes_from_matrix(X, batch_indices=0, labels=None):
        ne_cells = X.sum(axis=1) > 0
        to_keep = np.where(ne_cells)
        if not ne_cells.all():
            X = X[to_keep]
            removed_idx = np.where(~ne_cells)[0]
            print("Cells with zero expression in all genes considered were removed, the indices of the removed cells "
                  "in the expression matrix were:")
            print(removed_idx)
        local_mean, local_var = GeneExpressionDataset.library_size(X)
        batch_indices = batch_indices * np.ones((X.shape[0], 1)) if type(batch_indices) is int \
            else batch_indices[to_keep]
        labels = labels[to_keep].reshape(-1, 1) if labels is not None else np.zeros_like(batch_indices)
        return X, local_mean, local_var, batch_indices, labels