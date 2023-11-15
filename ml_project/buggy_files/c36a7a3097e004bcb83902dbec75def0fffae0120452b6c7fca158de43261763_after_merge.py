def run(n=1000):
    if n == "short":
        n = 50
    with get_garch_model():
        tr = sample(n, n_init=10000)
    return tr