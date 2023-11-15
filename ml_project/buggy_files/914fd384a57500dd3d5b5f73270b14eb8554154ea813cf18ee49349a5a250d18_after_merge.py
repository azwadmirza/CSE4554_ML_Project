    def load_data(self):
        result = super().load_data()

        for key, vcs in list(result.items()):
            try:
                version = vcs.get_version()
            except Exception as error:
                supported = False
                self.errors[vcs.name] = str(error)
            else:
                supported = vcs.is_supported()
                if not supported:
                    self.errors[vcs.name] = f"Outdated version: {version}"

            if not supported or not vcs.is_configured():
                result.pop(key)

        return result