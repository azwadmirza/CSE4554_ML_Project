    def __structuredFromJson(self, data):
        if len(data) == 0:
            return None
        else:
            return json.loads(data)