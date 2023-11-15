    def tile(cls, op):
        y_true, y_pred = op.y_true, op.y_pred
        for y in (op.y_true, op.y_pred):
            if isinstance(y, (Base, Entity)):
                if np.isnan(y.size):  # pragma: no cover
                    raise TilesError('input has unknown shape')

        check_consistent_length(y_true, y_pred)

        ctx = get_context()
        try:
            type_true, type_pred = ctx.get_chunk_results(
                [op.type_true.chunks[0].key,
                 op.type_pred.chunks[0].key])
        except KeyError:
            raise TilesError('type_true and type_pred '
                             'needs to be executed first')

        y_type = {type_true, type_pred}
        if y_type == {"binary", "multiclass"}:
            y_type = {"multiclass"}

        if len(y_type) > 1:
            raise ValueError(f"Classification metrics can't handle a mix of {type_true} "
                             f"and {type_pred} targets")

        # We can't have more than one value on y_type => The set is no more needed
        y_type = y_type.pop()

        # No metrics support "multiclass-multioutput" format
        if (y_type not in ["binary", "multiclass", "multilabel-indicator"]):
            raise ValueError(f"{y_type} is not supported")

        if y_type in ["binary", "multiclass"]:
            y_true = column_or_1d(y_true)
            y_pred = column_or_1d(y_pred)
            if y_type == "binary":
                unique_values = mt.union1d(y_true, y_pred)
                y_type = mt.where(mt.count_nonzero(unique_values) > 2,
                                  'multiclass', y_type)
        elif y_type.startswith('multilabel'):
            y_true = mt.tensor(y_true).tosparse()
            y_pred = mt.tensor(y_pred).tosparse()
            y_type = 'multilabel-indicator'

        if not isinstance(y_true, (Base, Entity)):
            y_true = mt.tensor(y_true)
        if not isinstance(y_pred, (Base, Entity)):
            y_pred = mt.tensor(y_pred)

        if not isinstance(y_type, TENSOR_TYPE):
            y_type = mt.tensor(y_type, dtype=object)

        y_type = recursive_tile(y_type)
        y_true = recursive_tile(y_true)
        y_pred = recursive_tile(y_pred)

        kws = [out.params for out in op.outputs]
        kws[0].update(dict(nsplits=(), chunks=[y_type.chunks[0]]))
        kws[1].update(dict(nsplits=y_true.nsplits, chunks=y_true.chunks,
                           shape=tuple(sum(sp) for sp in y_true.nsplits)))
        kws[2].update(dict(nsplits=y_pred.nsplits, chunks=y_pred.chunks,
                           shape=tuple(sum(sp) for sp in y_pred.nsplits)))
        new_op = op.copy()
        return new_op.new_tileables(op.inputs, kws=kws)