    def __init__(
        self,
        triples_factory: TriplesFactory,
        minimum_frequency: Optional[float] = None,
        symmetric: bool = True,
    ):
        """Index the inverse frequencies and the inverse relations in the triples factory.

        :param triples_factory: The triples factory to index.
        :param minimum_frequency: The minimum overlap between two relations' triples to consider them as inverses. The
         default value, 0.97, is taken from `Toutanova and Chen (2015) <https://www.aclweb.org/anthology/W15-4007/>`_,
         who originally described the generation of FB15k-237.
        """
        self.triples_factory = triples_factory
        if minimum_frequency is None:
            minimum_frequency = 0.97
        self.minimum_frequency = minimum_frequency

        # compute similarities
        if symmetric:
            rel, inv = triples_factory_to_sparse_matrices(triples_factory=triples_factory)
            self.candidate_duplicate_relations = get_candidate_pairs(a=rel, threshold=self.minimum_frequency)
            self.candidate_inverse_relations = get_candidate_pairs(a=rel, b=inv, threshold=self.minimum_frequency)
        else:
            raise NotImplementedError
        logger.info(
            f'identified {len(self.candidate_duplicate_relations)} candidate duplicate relationships'
            f' at similarity > {self.minimum_frequency} in {self.triples_factory}.',
        )
        logger.info(
            f'identified {len(self.candidate_inverse_relations)} candidate inverse pairs'
            f' at similarity > {self.minimum_frequency} in {self.triples_factory}',
        )
        self.candidates = set(self.candidate_duplicate_relations).union(self.candidate_inverse_relations)
        sizes = dict(zip(*triples_factory.mapped_triples[:, 1].unique(return_counts=True)))
        self.relations_to_delete = _select_by_most_pairs(
            components=_get_connected_components(pairs=((a, b) for (s, a, b) in self.candidates if (a != b))),
            size=sizes,
        )
        logger.info(f'identified {len(self.candidates)} from {self.triples_factory} to delete')