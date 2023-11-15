        def new_fun(X, **Ys):
            Xs = tf.unstack(X, axis=-1)
            fun_eval = old_fun(*Xs, **Ys)
            if tf.rank(fun_eval) < tf.rank(X):
                fun_eval = tf.expand_dims(fun_eval, axis=-1)
            return fun_eval