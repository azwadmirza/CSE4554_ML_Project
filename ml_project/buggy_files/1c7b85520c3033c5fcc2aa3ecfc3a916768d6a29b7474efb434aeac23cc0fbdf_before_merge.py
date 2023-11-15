def gen_random_seeds(n, random_state):
    assert isinstance(random_state, np.random.RandomState)
    return np.frombuffer(random_state.bytes(n * 4), dtype=np.uint32)