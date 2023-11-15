    def _prepare_sparse_dense_layers(
        self,
        feature_signatures: List[FeatureSignature],
        name: Text,
        reg_lambda: float,
        dense_dim: int,
    ) -> None:
        sparse = False
        dense = False
        for is_sparse, feature_dimension in feature_signatures:
            if is_sparse:
                sparse = True
            else:
                dense = True
                # if dense features are present
                # use the feature dimension of the dense features
                dense_dim = feature_dimension

        if sparse:
            self._tf_layers[f"sparse_to_dense.{name}"] = layers.DenseForSparse(
                units=dense_dim, reg_lambda=reg_lambda, name=name
            )
            if not dense:
                # create dense labels for the input to use in negative sampling
                self._tf_layers[f"sparse_to_dense_ids.{name}"] = layers.DenseForSparse(
                    units=2, trainable=False, name=f"sparse_to_dense_ids.{name}"
                )