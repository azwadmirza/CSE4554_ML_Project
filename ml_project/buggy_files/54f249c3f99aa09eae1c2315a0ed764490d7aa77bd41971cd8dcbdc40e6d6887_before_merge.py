    def to_tensorflow(self, max_text_len=30):
        """
        Transforms into tensorflow dataset

        Parameters
        ----------
        max_text_len: integer
            the maximum length of text strings that would be stored. Strings longer than this would be snipped

        """
        try:
            import tensorflow as tf
        except ImportError:
            pass

        def tf_gen(step=4):
            with dask.config.set(scheduler="sync"):
                for index in range(0, len(self), step):
                    arrs = [self[index : index + step].values() for i in range(1)]
                    arrs = list(map(lambda x: x._array, _flatten(arrs)))
                    arrs = dask.delayed(list, pure=False, nout=len(list(self.keys())))(
                        arrs
                    )
                    arrs = arrs.compute()
                    for ind, arr in enumerate(arrs):
                        if arr.dtype.type is np.str_:
                            arr = [
                                ([ord(x) for x in sample.tolist()[0:max_text_len]])
                                for sample in arr
                            ]
                            arr = np.array(
                                [
                                    np.pad(
                                        sample,
                                        (0, max_text_len - len(sample)),
                                        "constant",
                                        constant_values=(32),
                                    )
                                    for sample in arr
                                ]
                            )
                            arrs[ind] = arr

                    for i in range(step):
                        sample = {key: r[i] for key, r in zip(self[index].keys(), arrs)}
                        yield sample

        def tf_dtype(np_dtype):
            try:
                if "U" in np_dtype:
                    return tf.dtypes.as_dtype("string")
                return tf.dtypes.as_dtype(np_dtype)
            except Exception as e:
                return tf.variant

        output_shapes = {}
        output_types = {}
        for key in self.keys():
            output_types[key] = tf_dtype(self._tensors[key].dtype)
            output_shapes[key] = self._tensors[key].shape[1:]

            # if this is a string, we change the type to int, as it's going to become ascii. shape is also set to None
            if output_types[key] == tf.dtypes.as_dtype("string"):
                output_types[key] = tf.dtypes.as_dtype("int8")
                output_shapes[key] = None

        # TODO use None for dimensions you don't know the length tf.TensorShape([None])
        # FIXME Dataset Generator is not very good with multiprocessing but its good for fast tensorflow support
        return tf.data.Dataset.from_generator(
            tf_gen,
            output_types=output_types,
            # output_shapes=output_shapes,
        )