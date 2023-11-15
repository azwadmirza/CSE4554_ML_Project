def build_index(tensor, pk, dimension=None, index_path=None,
                need_shuffle=False, distance_metric='SquaredEuclidean',
                index_builder='SsgBuilder', index_builder_params=None,
                index_converter=None, index_converter_params=None,
                topk=None, storage_options=None,
                run=True, session=None, run_kwargs=None):
    tensor = validate_tensor(tensor)

    if dimension is None:
        dimension = tensor.shape[1]
    if index_builder_params is None:
        index_builder_params = {}
    if index_converter_params is None:
        index_converter_params = {}

    if need_shuffle:
        tensor = mt.random.permutation(tensor)

    if not isinstance(pk, (Base, Entity)):
        pk = mt.tensor(pk)

    op = ProximaBuilder(tensor=tensor, pk=pk, distance_metric=distance_metric,
                        index_path=index_path, dimension=dimension,
                        index_builder=index_builder,
                        index_builder_params=index_builder_params,
                        index_converter=index_converter,
                        index_converter_params=index_converter_params,
                        topk=topk, storage_options=storage_options)
    result = op(tensor, pk)
    if run:
        return result.execute(session=session, **(run_kwargs or dict()))
    else:
        return result