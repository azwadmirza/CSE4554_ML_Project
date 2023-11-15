    def __init__(self, hparams, iterator_creator, graph=None):
        """
        Initializing the model. Create common logics which are needed by all deeprec models, such as loss function, parameter set.
        :param hparams:  a tf.contrib.training.HParams object, hold the entire set of hyperparameters.
        """
        if not graph:
            self.graph = tf.Graph()
        else:
            self.graph = graph

        self.iterator = iterator_creator(hparams, self.graph)

        with self.graph.as_default():
            self.hparams = hparams

            self.layer_params = []
            self.embed_params = []
            self.cross_params = []
            self.layer_keeps = tf.placeholder(tf.float32, name="layer_keeps")
            self.keep_prob_train = None
            self.keep_prob_test = None
            self.is_train_stage = tf.placeholder(tf.bool, shape=(), name="is_training")

            self.initializer = self._get_initializer()

            self.logit = self._build_graph()
            self.pred = self._get_pred(self.logit, self.hparams.method)

            self.loss = self._get_loss()
            self.saver = tf.train.Saver(max_to_keep=self.hparams.epochs)
            self.update = self._build_train_opt()
            self.init_op = tf.global_variables_initializer()
            self.merged = self._add_summaries()

        self.sess = tf.Session(graph=self.graph)
        self.sess.run(self.init_op)