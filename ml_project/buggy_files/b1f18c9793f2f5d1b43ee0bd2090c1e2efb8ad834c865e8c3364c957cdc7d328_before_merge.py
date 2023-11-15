def get_device_name(device_handle):
    """Get GPU device name"""
    try:
        return pynvml.nvmlDeviceGetName(device_handle)
    except pynvml.NVMlError:
        return "NVIDIA"