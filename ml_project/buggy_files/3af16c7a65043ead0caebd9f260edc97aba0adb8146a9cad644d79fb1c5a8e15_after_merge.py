def sigmoid_cross_entropy_with_logits(x,
                                      label,
                                      ignore_index=kIgnoreIndex,
                                      name=None,
                                      normalize=False):
    """
    ${comment}

    Args:
        x(${x_type}): ${x_comment}
        label(${label_type}): ${label_comment}
        ignore_index(&{ignore_index}): ${ignore_index_comment}
        name(basestring|None): Name of the output.
        normalize(bool): If true, divide the output by the number of
            targets != ignore_index.

    Returns:
        out(${out_type}): ${out_comment}

    Examples:
        .. code-block:: python

            input = fluid.layers.data(
                name='data', shape=[10], dtype='float32')
            label = fluid.layers.data(
                name='data', shape=[10], dtype='float32')
            loss = fluid.layers.sigmoid_cross_entropy_with_logits(
                x=input,
                label=label,
                ignore_index=-1,
                normalize=True) # or False
            # loss = fluid.layers.reduce_sum(loss) # summation of loss
    """

    helper = LayerHelper("sigmoid_cross_entropy_with_logits", **locals())

    if name is None:
        out = helper.create_variable_for_type_inference(dtype=x.dtype)
    else:
        out = helper.create_variable(
            name=name, dtype=x.dtype, persistable=False)

    helper.append_op(
        type="sigmoid_cross_entropy_with_logits",
        inputs={"X": x,
                "Label": label},
        attrs={"ignore_index": ignore_index,
               'normalize': normalize},
        outputs={"Out": out})
    return out