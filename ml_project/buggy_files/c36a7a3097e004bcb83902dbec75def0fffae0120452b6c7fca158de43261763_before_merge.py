def run(n=1000):
    if n == "short":
        n = 50
    with garch:
        tr = sample(n)