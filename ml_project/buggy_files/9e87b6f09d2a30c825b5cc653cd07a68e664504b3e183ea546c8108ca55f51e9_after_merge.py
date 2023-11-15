    def wrapper(old_fun):
        def new_fun(X, **Ys):
            Xs = tf.unstack(X, axis=-1)
            fun_eval = old_fun(*Xs, **Ys)
            return tf.cond(
                pred=tf.less(tf.rank(fun_eval), tf.rank(X)),
                true_fn=lambda: fun_eval[..., tf.newaxis],
                false_fn=lambda: fun_eval,
            )

        return new_fun