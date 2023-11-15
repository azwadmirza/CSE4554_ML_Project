    def load_data(self):
        result = super().load_data()

        for key, vcs in list(result.items()):
            try:
                supported = vcs.is_supported()
            except Exception as error:
                supported = False
                self.errors[vcs.name] = str(error)

            if not supported:
                result.pop(key)

        return result