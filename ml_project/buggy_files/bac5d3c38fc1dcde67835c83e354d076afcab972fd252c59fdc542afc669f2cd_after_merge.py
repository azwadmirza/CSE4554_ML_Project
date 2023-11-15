    def __read_metadata(self, filepath: str, federated_only: bool):

        from nucypher.characters.lawful import Ursula

        try:
            with open(filepath, "rb") as seed_file:
                seed_file.seek(0)
                node_bytes = self.deserializer(seed_file.read())
                node = Ursula.from_bytes(node_bytes, federated_only=federated_only)  # TODO: #466
        except FileNotFoundError:
            raise self.UnknownNode
        return node