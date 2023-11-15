    def __init__(self):
        # `autoreset` allows us to not have to sent reset sequences for every
        # string. `strip` lets us preserve color when redirecting.
        colorama.init(autoreset=True, strip=False)