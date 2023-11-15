    def __structuredFromJson(self, data):
        if len(data) == 0:
            return None
        else:
            if atLeastPython3 and isinstance(data, bytes):
                data=data.decode("utf-8")
            return json.loads(data)