def _get_memory(string, offset):
    return memoryview(string)[offset:]