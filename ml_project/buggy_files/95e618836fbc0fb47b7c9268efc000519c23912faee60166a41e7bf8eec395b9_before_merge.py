def maxpool2d(a_sh, kernel_size: int = 1, stride: int = 1, padding: int = 0):
    """Applies a 2D max pooling over an input signal composed of several input planes.
    This interface is similar to torch.nn.MaxPool2D.
    Args:
        kernel_size: the size of the window to take a max over
        stride: the stride of the window
        padding: implicit zero padding to be added on both sides
    """
    assert (
        a_sh.dtype != "custom"
    ), "`custom` dtype shares are unsupported in SecureNN, use dtype = `long` or `int` instead"
    assert len(a_sh.shape) == 4

    # Change to tuple if not one
    kernel = torch.nn.modules.utils._pair(kernel_size)
    stride = torch.nn.modules.utils._pair(stride)
    padding = torch.nn.modules.utils._pair(padding)

    # TODO: support dilation.
    dilation = torch.nn.modules.utils._pair(1)

    # Extract a few useful values
    batch_size, nb_channels, nb_rows_in, nb_cols_in = a_sh.shape

    # Calculate output shapes
    nb_rows_out = int(
        (nb_rows_in + 2 * padding[0] - dilation[0] * (kernel[0] - 1) - 1) / stride[0] + 1
    )
    nb_cols_out = int(
        (nb_cols_in + 2 * padding[1] - dilation[1] * (kernel[1] - 1) - 1) / stride[1] + 1
    )

    # Apply padding to the input
    if padding != (0, 0):
        a_sh = torch.nn.functional.pad(
            a_sh, (padding[1], padding[1], padding[0], padding[0]), "constant"
        )
        # Update shape after padding
        nb_rows_in += 2 * padding[0]
        nb_cols_in += 2 * padding[1]

    res = []
    # TODO: make this operation more efficient in order to be used with cnn modules.
    for batch in range(batch_size):
        for channel in range(nb_channels):
            for r_in in range(0, nb_rows_in - (kernel[0] - 1), stride[0]):
                for c_in in range(0, nb_cols_in - (kernel[1] - 1), stride[1]):
                    m, _ = maxpool(
                        a_sh[batch, channel, r_in : r_in + kernel[0], c_in : c_in + kernel[1]].child
                    )
                    res.append(m.wrap())

    res = torch.stack(res).reshape(batch_size, nb_channels, nb_rows_out, nb_cols_out)
    return res