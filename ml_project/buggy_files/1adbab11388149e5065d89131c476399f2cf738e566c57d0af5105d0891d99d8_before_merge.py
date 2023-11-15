    def begin_training(self, get_gold_tuples=None, sgd=None, **cfg):
        """Allocate models, pre-process training data and acquire a trainer and
        optimizer. Used as a contextmanager.

        get_gold_tuples (function): Function returning gold data
        **cfg: Config parameters.
        RETURNS: An optimizer
        """
        if get_gold_tuples is None:
            get_gold_tuples = lambda: []
        # Populate vocab
        else:
            for _, annots_brackets in get_gold_tuples():
                for annots, _ in annots_brackets:
                    for word in annots[1]:
                        _ = self.vocab[word]
        contexts = []
        if cfg.get('device', -1) >= 0:
            device = util.use_gpu(cfg['device'])
            if self.vocab.vectors.data.shape[1] >= 1:
                self.vocab.vectors.data = Model.ops.asarray(
                    self.vocab.vectors.data)
        else:
            device = None
        link_vectors_to_models(self.vocab)
        if sgd is None:
            sgd = create_default_optimizer(Model.ops)
        self._optimizer = sgd
        for name, proc in self.pipeline:
            if hasattr(proc, 'begin_training'):
                proc.begin_training(get_gold_tuples(),
                                    pipeline=self.pipeline,
                                    sgd=self._optimizer,
                                    **cfg)
        return self._optimizer