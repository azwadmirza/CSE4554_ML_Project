def convert(topology, backend, test_input, device, extra_config={}):
    """
    This function is used to convert a `onnxconverter_common.topology.Topology` object into a *backend* model.

    Args:
        topology: The `onnxconverter_common.topology.Topology` object that will be converted into a backend model
        backend: Which backend the model should be run on
        test_input: Inputs for PyTorch model tracing
        device: Which device the translated model will be run on
        extra_config: Extra configurations to be used by individual operator converters

    Returns:
        A model implemented in the selected backend
    """
    assert topology is not None, "Cannot convert a Topology object of type None."
    assert backend is not None, "Cannot convert a Topology object into backend None."
    assert device is not None, "Cannot convert a Topology object into device None."

    tvm_backend = None
    operator_map = {}

    if tvm_installed():
        import tvm

        tvm_backend = tvm.__name__

    for operator in topology.topological_operator_iterator():
        converter = get_converter(operator.type)
        if convert is None:
            raise MissingConverter(
                "Unable to find converter for {} type {} with extra config: {}.".format(
                    operator.type, type(getattr(operator, "raw_model", None)), extra_config
                )
            )

        if backend == onnx.__name__:
            # vers = LooseVersion(torch.__version__)
            # allowed_min = LooseVersion("1.6.0")
            # Pytorch <= 1.6.0 has a bug with exporting GEMM into ONNX.
            # For the moment only tree_trav is enabled for pytorch <= 1.6.0
            # if vers < allowed_min:
            extra_config[constants.TREE_IMPLEMENTATION] = "tree_trav"
        operator_map[operator.full_name] = converter(operator, device, extra_config)

    # Set the parameters for the model / container
    n_threads = None if constants.N_THREADS not in extra_config else extra_config[constants.N_THREADS]

    # We set the number of threads for torch here to avoid errors in case we JIT.
    # We set intra op concurrency while we force operators to run sequentially.
    # We can revise this later, but in general we don't have graphs requireing inter-op parallelism.
    if n_threads is not None:
        if torch.get_num_interop_threads() != 1:
            torch.set_num_interop_threads(1)
        torch.set_num_threads(n_threads)

    operators = list(topology.topological_operator_iterator())
    executor = Executor(
        topology.raw_model.input_names, topology.raw_model.output_names, operator_map, operators, extra_config
    ).eval()

    # if constants.REMAINDER_SIZE is present in extra_config, we are in the convert_batch mode.
    remainder_model = None
    remainder_size = None if constants.REMAINDER_SIZE not in extra_config else extra_config[constants.REMAINDER_SIZE]

    if backend == onnx.__name__:
        onnx_model_name = output_model_name = None
        target_opset = 11

        # Set optional configuration options for ONNX if any.
        if constants.ONNX_OUTPUT_MODEL_NAME in extra_config:
            onnx_model_name = extra_config[constants.ONNX_OUTPUT_MODEL_NAME]
            output_model_name = onnx_model_name + ".onnx"
        if constants.ONNX_TARGET_OPSET in extra_config:
            target_opset = extra_config[constants.ONNX_TARGET_OPSET]
        if output_model_name is None:
            output_model_name = str(uuid4().hex) + ".onnx"

        # Put the tracing test input into the right format.
        batch_trace_input, _ = _get_trace_input_from_test_input(test_input, remainder_size, extra_config)

        # Generate the ONNX models
        torch.onnx.export(
            executor,
            batch_trace_input,
            output_model_name,
            input_names=topology.raw_model.input_names,
            output_names=topology.raw_model.output_names,
            keep_initializers_as_inputs=False,
            opset_version=target_opset,
            do_constant_folding=True,
        )
        hb_model = onnx.load(output_model_name)
        os.remove(output_model_name)

        # Set the ONNX model name if any.
        if onnx_model_name is not None:
            hb_model.graph.name = onnx_model_name

        # Fix the model to use arbitrary batch dimensions
        def fix_dim(dim):
            updated = False
            if dim.HasField("dim_value"):
                dim.Clear()
                updated = True
                dim.dim_param = "sym"

            return updated

        def fix_value_info(value):
            num_fixed = 0
            if value.type.HasField("tensor_type"):
                shape = value.type.tensor_type.shape
                if shape:
                    dim = shape.dim[0]
                    if fix_dim(dim):
                        num_fixed += 1

            return num_fixed

        def fix_graph(graph):
            num_fixed = 0
            for input in graph.input:
                num_fixed += fix_value_info(input)

            for output in graph.output:
                num_fixed += fix_value_info(output)

            for node in graph.node:
                for attr in node.attribute:
                    if attr.HasField("g"):
                        num_fixed += fix_graph(attr.g)

            return num_fixed

        fix_graph(hb_model.graph)
    elif backend == tvm_backend:
        # Pick the proper target.
        if device == "cuda":
            target = tvm.target.cuda()
            ctx = tvm.gpu()
        elif device == "cpu":
            target = "llvm"
            ctx = tvm.cpu()
        elif "llvm" in device:
            target = device
            ctx = tvm.cpu()
        else:
            raise RuntimeError("Device {} not recognized".format(device))

        # Get configuration parameters.
        # 50 is a good depth for operator fusion. More than that will probably hurt performance.
        # https://github.com/microsoft/hummingbird/issues/232#issuecomment-697979508
        config = {"relay.FuseOps.max_depth": 50}

        if constants.TVM_MAX_FUSE_DEPTH in extra_config:
            config["relay.FuseOps.max_depth"] = extra_config[constants.TVM_MAX_FUSE_DEPTH]

        # First we need to generate the torchscript model.
        batch_trace_input, remainder_trace_input = _get_trace_input_from_test_input(test_input, remainder_size, extra_config)

        tvm_model = _compile_to_tvm(topology, executor, batch_trace_input, target, ctx, config, extra_config)

        if remainder_trace_input is not None:
            remainder_model = _compile_to_tvm(topology, executor, remainder_trace_input, target, ctx, config, extra_config)

        # In the container we will be using the context to properly configure the input tensors.
        extra_config[constants.TVM_CONTEXT] = ctx
        extra_config[constants.TVM_INPUT_NAMES] = topology.raw_model.input_names

        hb_model = tvm_model
    else:
        # Set the device for the model.
        if device != "cpu":
            if backend == torch.__name__ or torch.jit.__name__:
                executor = executor.to(device)

        # If the backend is tochscript, jit the model.
        if backend == torch.jit.__name__:
            trace_input, _ = _get_trace_input_from_test_input(test_input, remainder_size, extra_config)
            executor = _jit_trace(executor, trace_input, device, extra_config)
            torch.jit.optimized_execution(executor)

        hb_model = executor

    # Return if the container is not needed.
    if constants.CONTAINER in extra_config and not extra_config[constants.CONTAINER]:
        return hb_model

    # We scan the operators backwards until we find an operator with a defined type.
    # This is necessary because ONNX models can have arbitrary operators doing casting, reshaping etc.
    idx = len(operators) - 1
    while (
        idx >= 0
        and not operator_map[operators[idx].full_name].regression
        and not operator_map[operators[idx].full_name].classification
        and not operator_map[operators[idx].full_name].anomaly_detection
        and not operator_map[operators[idx].full_name].transformer
    ):
        idx -= 1

    assert idx >= 0, "Cannot detect container type. Please fill an issue at https://github.com/microsoft/hummingbird."

    # If is a transformer, we need to check whether there is another operator type before.
    # E.g., normalization after classification.
    tmp_idx = idx
    if operator_map[operators[idx].full_name].transformer:
        while (
            idx >= 0
            and not operator_map[operators[idx].full_name].regression
            and not operator_map[operators[idx].full_name].classification
            and not operator_map[operators[idx].full_name].anomaly_detection
        ):
            idx -= 1
        if idx < 0:
            idx = tmp_idx

    # Get the proper container type.
    if operator_map[operators[idx].full_name].regression:
        # We are doing a regression task.
        if backend == torch.jit.__name__:
            container = TorchScriptSklearnContainerRegression
        elif backend == onnx.__name__:
            container = ONNXSklearnContainerRegression
        elif backend == tvm_backend:
            container = TVMSklearnContainerRegression
        else:
            container = PyTorchSklearnContainerRegression
    elif operator_map[operators[idx].full_name].anomaly_detection:
        # We are doing anomaly detection.
        if backend == torch.jit.__name__:
            container = TorchScriptSklearnContainerAnomalyDetection
        elif backend == onnx.__name__:
            container = ONNXSklearnContainerAnomalyDetection
        elif backend == tvm_backend:
            container = TVMSklearnContainerAnomalyDetection
        else:
            container = PyTorchSklearnContainerAnomalyDetection
    elif operator_map[operators[idx].full_name].transformer:
        # We are just transforming the input data.
        if backend == torch.jit.__name__:
            container = TorchScriptSklearnContainerTransformer
        elif backend == onnx.__name__:
            container = ONNXSklearnContainerTransformer
        elif backend == tvm_backend:
            container = TVMSklearnContainerTransformer
        else:
            container = PyTorchSklearnContainerTransformer
    else:
        # We are doing a classification task.
        if backend == torch.jit.__name__:
            container = TorchScriptSklearnContainerClassification
        elif backend == onnx.__name__:
            container = ONNXSklearnContainerClassification
        elif backend == tvm_backend:
            container = TVMSklearnContainerClassification
        else:
            container = PyTorchSklearnContainerClassification

    n_threads = None if constants.N_THREADS not in extra_config else extra_config[constants.N_THREADS]
    batch_size = None if constants.TEST_INPUT not in extra_config else _get_batch_size(test_input)
    hb_container = container(hb_model, n_threads, batch_size, extra_config=extra_config)

    if remainder_model:
        aux_container = container(remainder_model, n_threads, remainder_size, extra_config=extra_config)
        return BatchContainer(hb_container, aux_container)
    elif remainder_size is not None and remainder_size > 0:
        # remainder_size is non zero but remainder_model is not created
        # -> torch backend case
        aux_container = container(hb_model, n_threads, remainder_size, extra_config=extra_config)
        return BatchContainer(hb_container, aux_container)
    elif remainder_size is not None:
        # remainder_size is not None but remainder_model is not created
        # -> remainder_size must be zero (no need to create remainder_model)
        assert remainder_size == 0, "remainder_size is non zero but no remainder_model has been created"
        # remainder_size is not None only if called by convert_batch(...), so we return BatchContainer
        # for this code path, even though there is no remainder_model created.
        return BatchContainer(hb_container)

    return hb_container