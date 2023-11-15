        def tf_dtype(np_dtype):
            try:
                if "U" in np_dtype:
                    return tf.dtypes.as_dtype("string")
                return tf.dtypes.as_dtype(np_dtype)
            except Exception as e:
                return tf.variant