    def assign_average_vars(self, var_list):
        """Assign variables in var_list with their respective averages.

        Args:
            var_list: List of model variables to be assigned to their average.

        Returns:
            assign_op: The op corresponding to the assignment operation of
            variables to their average.

        Example:
        ```python
        model = tf.Sequential([...])
        opt = tfa.optimizers.SWA(
                tf.keras.optimizers.SGD(lr=2.0), 100, 10)
        model.compile(opt, ...)
        model.fit(x, y, ...)

        # Update the weights to their mean before saving
        opt.assign_average_vars(model.variables)

        model.save('model.h5')
        ```
        """
        assign_ops = []
        for var in var_list:
            try:
                assign_ops.append(
                    var.assign(
                        self.get_slot(var, "average"), use_locking=self._use_locking
                    )
                )
            except Exception as e:
                warnings.warn("Unable to assign average slot to {} : {}".format(var, e))
        return tf.group(assign_ops)