    def _combine_sparse_dense_features(
        self,
        features: List[Union[tf.Tensor, tf.SparseTensor]],
        mask: tf.Tensor,
        name: Text,
    ) -> tf.Tensor:
        dense_features = []

        dense_dim = self.dense_dim[name]
        # if dense features are present use the feature dimension of the dense features
        for f in features:
            if not isinstance(f, tf.SparseTensor):
                dense_dim = f.shape[-1]
                break

        for f in features:
            if isinstance(f, tf.SparseTensor):
                dense_features.append(
                    train_utils.tf_dense_layer_for_sparse(f, dense_dim, name, self.C2)
                )
            else:
                dense_features.append(f)

        output = tf.concat(dense_features, axis=-1) * mask
        output = tf.squeeze(output, axis=1)

        return output