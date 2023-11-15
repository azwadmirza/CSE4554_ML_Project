    def get_signature(self) -> Dict[Text, List[FeatureSignature]]:
        """Get signature of RasaModelData.

        Signature stores the shape and whether features are sparse or not for every key.
        """

        return {
            key: [
                FeatureSignature(
                    True if isinstance(v[0], scipy.sparse.spmatrix) else False,
                    v[0].shape,
                )
                for v in values
            ]
            for key, values in self.data.items()
        }