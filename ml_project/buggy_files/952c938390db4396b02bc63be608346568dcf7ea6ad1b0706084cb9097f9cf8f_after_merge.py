    def _get_node_interface(self, endpoint: str) -> SubstrateInterface:
        """Get an instance of SubstrateInterface, a specialized class in
        interfacing with a Substrate node that deals with SCALE encoding/decoding,
        metadata parsing, type registry management and versioning of types.

        May raise (most common):
        - RemoteError: from RequestException, problems requesting the url.
        - FileNotFound: via `load_type_registry_preset()` if it doesn't exist
        a preset file for the given `type_registry_preset` argument.
        - ValueError and TypeError: invalid constructor arguments.
        """
        si_attributes = self.chain.substrate_interface_attributes()
        try:
            node_interface = SubstrateInterface(
                url=endpoint,
                type_registry_preset=si_attributes.type_registry_preset,
            )
        except requests.exceptions.RequestException as e:
            message = (
                f'{self.chain} could not connect to node at endpoint: {endpoint}. '
                f'Connection error: {str(e)}.'
            )
            log.error(message)
            raise RemoteError(message) from e
        except (FileNotFoundError, ValueError, TypeError) as e:
            message = (
                f'{self.chain} could not connect to node at endpoint: {endpoint}. '
                f'Unexpected error during SubstrateInterface instantiation: {str(e)}.'
            )
            log.error(message)
            raise RemoteError('Invalid SubstrateInterface instantiation') from e

        return node_interface