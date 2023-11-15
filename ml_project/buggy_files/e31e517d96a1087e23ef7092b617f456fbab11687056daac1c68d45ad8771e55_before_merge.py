    def _wrap_train_tuple(data, label, sample_weight=None, init_score=None):
        return TrainTuple(data, label, sample_weight, init_score)