def _get_memory(data):
    mv = memoryview(data)
    if mv.shape:
        return mv
    # No shape, probably working with a ctypes object,
    # or something else exotic that supports the buffer interface
    return mv.tobytes()