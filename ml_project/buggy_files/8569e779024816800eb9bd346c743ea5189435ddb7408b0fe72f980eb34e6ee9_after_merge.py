def conv2d_winograd_nhwc_cuda(
    data, weight, strides, padding, dilation, out_dtype, pre_computed=False
):
    """Conv2D Winograd in NHWC layout.
    This is a clean version to be used by the auto-scheduler for both CPU and GPU.
    """
    tile_size = _infer_tile_size(data, weight, layout="NHWC")
    return _conv2d_winograd_nhwc_impl(
        data, weight, strides, padding, dilation, out_dtype, tile_size, pre_computed
    )