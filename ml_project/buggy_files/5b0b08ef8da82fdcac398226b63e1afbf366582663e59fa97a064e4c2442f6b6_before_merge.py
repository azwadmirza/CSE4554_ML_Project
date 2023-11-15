    def serialize(self) -> JsonDict:
        return {'.class': 'TypeType', 'item': self.item.serialize()}