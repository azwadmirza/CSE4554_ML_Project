    def _set_inputs(self, inputs):
        super()._set_inputs(inputs)
        it = iter(inputs)
        for attr in ['_data', '_label', '_sample_weight', '_init_score']:
            if getattr(self, attr) is not None:
                setattr(self, attr, next(it))
        for attr in ['_eval_datas', '_eval_labels', '_eval_sample_weights', '_eval_init_scores']:
            new_list = []
            for c in getattr(self, attr, None) or []:
                if c is not None:
                    new_list.append(next(it))
            setattr(self, attr, new_list or None)