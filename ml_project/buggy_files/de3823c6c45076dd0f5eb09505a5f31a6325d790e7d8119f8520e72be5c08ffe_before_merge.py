    def tile(cls, op):
        ctx = get_context()
        try:
            type_true = ctx.get_chunk_results([op.type_true.chunks[0].key])[0]
        except KeyError:
            raise TilesError('type_true needed to be executed first')

        y_true, y_pred = op.y_true, op.y_pred
        if type_true.item().startswith('multilabel'):
            differing_labels = mt.count_nonzero(y_true - y_pred, axis=1)
            score = mt.equal(differing_labels, 0)
        else:
            score = mt.equal(y_true, y_pred)

        result = _weighted_sum(score, op.sample_weight, op.normalize)
        return [recursive_tile(result)]