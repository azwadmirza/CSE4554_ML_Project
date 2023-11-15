    def simplify(tensor: "AdditiveSharingTensor") -> tuple:
        """
        This function takes the attributes of a AdditiveSharingTensor and saves them in a tuple
        Args:
            tensor (AdditiveSharingTensor): a AdditiveSharingTensor
        Returns:
            tuple: a tuple holding the unique attributes of the additive shared tensor
        Examples:
            data = simplify(tensor)
        """

        chain = None
        if hasattr(tensor, "child"):
            chain = sy.serde._simplify(tensor.child)

        # Don't delete the remote values of the shares at simplification
        tensor.set_garbage_collect_data(False)

        return (tensor.id, tensor.field, tensor.crypto_provider.id, chain)