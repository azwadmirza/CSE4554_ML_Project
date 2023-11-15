    def __call__(self, tf_method):
        @wraps(tf_method)
        def runnable(instance, *np_args):
            graph_name = '_' + tf_method.__name__ + '_graph'
            if not hasattr(instance, graph_name):
                if instance._needs_recompile:
                    instance._compile()  # ensures free_vars is up-to-date.
                self.tf_args = [tf.placeholder(*a) for a in self.tf_arg_tuples]
                with instance.tf_mode():
                    graph = tf_method(instance, *self.tf_args)
                setattr(instance, graph_name, graph)
            feed_dict = dict(zip(self.tf_args, np_args))
            feed_dict[instance._free_vars] = instance.get_free_state()
            graph = getattr(instance, graph_name)
            return instance._session.run(graph, feed_dict=feed_dict)
        return runnable