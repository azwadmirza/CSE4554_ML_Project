    def _wrap_train_tuple(cls, data, label, sample_weight=None, init_score=None):
        data = cls._convert_tileable(data)
        label = cls._convert_tileable(label)
        sample_weight = cls._convert_tileable(sample_weight)
        init_score = cls._convert_tileable(init_score)
        return TrainTuple(data, label, sample_weight, init_score)