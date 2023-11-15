    def get_inverse_relation_id(self, relation: Union[str, int]) -> int:
        """Get the inverse relation identifier for the given relation."""
        if not self.create_inverse_triples:
            raise ValueError('Can not get inverse triple, they have not been created.')
        relation = next(iter(self.relations_to_ids(relations=[relation])))
        return self._get_inverse_relation_id(relation)