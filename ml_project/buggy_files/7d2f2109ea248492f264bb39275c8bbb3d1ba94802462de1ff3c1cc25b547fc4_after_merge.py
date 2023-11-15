def random_state(num):
    """
    Return a random quantum state from the uniform (Haar) measure on
    state space.

    Args:
        num (int): the number of qubits
    Returns:
        ndarray:  state(2**num) a random quantum state.
    """
    # Random array over interval (0, 1]
    x = np.random.random(1 << num)
    x += x == 0
    x = -np.log(x)
    sumx = sum(x)
    phases = np.random.random(1 << num)*2.0*np.pi
    return np.sqrt(x/sumx)*np.exp(1j*phases)