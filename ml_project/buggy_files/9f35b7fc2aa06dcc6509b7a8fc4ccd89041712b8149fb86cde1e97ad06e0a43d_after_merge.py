def get_gpu_memory_map():
    """Get the current gpu usage.

    Returns
    -------
    usage: dict
        Keys are device ids as integers.
        Values are memory usage as integers in MB.
    """
    result = subprocess.run(
        [
            'nvidia-smi',
            '--query-gpu=memory.used',
            '--format=csv,nounits,noheader',
        ],
        encoding='utf-8',
        capture_output=True,
        check=True)
    # Convert lines into a dictionary
    gpu_memory = [int(x) for x in result.stdout.strip().split(os.linesep)]
    gpu_memory_map = {f'gpu_{index}': memory for index, memory in enumerate(gpu_memory)}
    return gpu_memory_map