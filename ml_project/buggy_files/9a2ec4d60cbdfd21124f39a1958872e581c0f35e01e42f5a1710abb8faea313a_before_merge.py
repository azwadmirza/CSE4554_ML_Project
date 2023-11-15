    def __init__(self, model_type=None, data=None, label=None, sample_weight=None, init_score=None,
                 eval_datas=None, eval_labels=None, eval_sample_weights=None, eval_init_scores=None,
                 params=None, kwds=None, lgbm_endpoints=None, lgbm_port=None, tree_learner=None,
                 timeout=None, **kw):
        super().__init__(_model_type=model_type, _params=params, _data=data, _label=label,
                         _sample_weight=sample_weight, _init_score=init_score, _eval_datas=eval_datas,
                         _eval_labels=eval_labels, _eval_sample_weights=eval_sample_weights,
                         _eval_init_scores=eval_init_scores, _kwds=kwds, _lgbm_endpoints=lgbm_endpoints,
                         _lgbm_port=lgbm_port, _tree_learner=tree_learner, _timeout=timeout,
                         **kw)
        if self.output_types is None:
            self.output_types = [OutputType.object]