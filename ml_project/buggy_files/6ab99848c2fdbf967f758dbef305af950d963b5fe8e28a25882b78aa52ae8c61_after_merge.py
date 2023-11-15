    def get_object(self, path):
        for item in self.items:
            if item.text == path[-1]:
                if item.parents == path[:-1]:
                    return item