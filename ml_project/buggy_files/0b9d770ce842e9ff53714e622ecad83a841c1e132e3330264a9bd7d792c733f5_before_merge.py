def get_task_specific_params(args, task_name):
    """ Search args for parameters specific to task.
    Args:
        args: main-program args, a config.Params object
        task_name: (string)
    Returns:
        AllenNLP Params object of task-specific params.
    """

    def _get_task_attr(attr_name, default=None):
        return config.get_task_attr(args, task_name, attr_name, default)

    params = {}
    params["cls_type"] = _get_task_attr("classifier")
    params["d_hid"] = _get_task_attr("classifier_hid_dim")
    params["d_proj"] = _get_task_attr("d_proj")
    params["shared_pair_attn"] = args.shared_pair_attn
    if args.shared_pair_attn:
        params["attn"] = args.pair_attn
        params["d_hid_attn"] = args.d_hid_attn
        params["dropout"] = args.classifier_dropout
    else:
        params["attn"] = _get_task_attr("pair_attn")
        params["d_hid_attn"] = _get_task_attr("d_hid_attn")
        params["dropout"] = _get_task_attr("classifier_dropout")

    # Used for edge probing. Other tasks can safely ignore.
    params["cls_loss_fn"] = _get_task_attr("classifier_loss_fn")
    params["cls_span_pooling"] = _get_task_attr("classifier_span_pooling")
    params["edgeprobe_cnn_context"] = _get_task_attr("edgeprobe_cnn_context")

    # For NLI probing tasks, might want to use a classifier trained on
    # something else (typically 'mnli').
    cls_task_name = _get_task_attr("use_classifier")
    # default to this task
    params["use_classifier"] = cls_task_name or task_name

    return Params(params)