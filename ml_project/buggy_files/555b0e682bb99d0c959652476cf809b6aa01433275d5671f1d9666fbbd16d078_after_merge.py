    def __init__(self, ini_dict: dict = None):
        self._style = self._style_name = None
        self._detyped = None
        self._d = dict()
        self._targets = set()
        if ini_dict:
            for key, value in ini_dict.items():
                self[key] = value  # in case init includes ln=target