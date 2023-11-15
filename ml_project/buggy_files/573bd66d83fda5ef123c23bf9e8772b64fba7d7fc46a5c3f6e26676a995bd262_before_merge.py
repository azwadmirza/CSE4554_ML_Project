    def __init__(self, data, name, **kwargs):
        self._data = data
        self._name = name
        self._validated_name = None
        self._kwargs = kwargs