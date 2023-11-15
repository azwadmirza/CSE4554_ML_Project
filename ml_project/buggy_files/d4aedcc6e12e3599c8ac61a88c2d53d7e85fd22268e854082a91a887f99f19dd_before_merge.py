    def execute(cls, ctx, op: "LGBMTrain"):
        if op.merge:
            return super().execute(ctx, op)

        from lightgbm.basic import _safe_call, _LIB

        data_val = ctx[op.data.key]
        label_val = ctx[op.label.key]
        sample_weight_val = ctx[op.sample_weight.key] if op.sample_weight is not None else None
        init_score_val = ctx[op.init_score.key] if op.init_score is not None else None

        if op.eval_datas is None:
            eval_set, eval_sample_weight, eval_init_score = None, None, None
        else:
            eval_set, eval_sample_weight, eval_init_score = [], [], []
            for data, label in zip(op.eval_datas, op.eval_labels):
                eval_set.append((ctx[data.key], ctx[label.key]))
            for weight in op.eval_sample_weights:
                eval_sample_weight.append(ctx[weight.key] if weight is not None else None)
            for score in op.eval_init_scores:
                eval_init_score.append(ctx[score.key] if score is not None else None)

            eval_set = eval_set or None
            eval_sample_weight = eval_sample_weight or None
            eval_init_score = eval_init_score or None

        params = op.params.copy()
        if ctx.running_mode == RunningMode.distributed:
            params['machines'] = ','.join(op.lgbm_endpoints)
            params['time_out'] = op.timeout
            params['num_machines'] = len(op.lgbm_endpoints)
            params['local_listen_port'] = op.lgbm_port

            if (op.tree_learner or '').lower() not in {'data', 'feature', 'voting'}:
                logger.warning('Parameter tree_learner not set or set to incorrect value '
                               f'{op.tree_learner}, using "data" as default')
                params['tree_learner'] = 'data'
            else:
                params['tree_learner'] = op.tree_learner

        try:
            model_cls = get_model_cls_from_type(op.model_type)
            model = model_cls(**params)
            model.fit(data_val, label_val, sample_weight=sample_weight_val, init_score=init_score_val,
                      eval_set=eval_set, eval_sample_weight=eval_sample_weight,
                      eval_init_score=eval_init_score, **op.kwds)

            if op.model_type == LGBMModelType.RANKER or \
                    op.model_type == LGBMModelType.REGRESSOR:
                model.set_params(out_dtype_=np.dtype('float'))
            elif hasattr(label_val, 'dtype'):
                model.set_params(out_dtype_=label_val.dtype)
            else:
                model.set_params(out_dtype_=label_val.dtypes[0])

            ctx[op.outputs[0].key] = pickle.dumps(model)
        finally:
            _safe_call(_LIB.LGBM_NetworkFree())