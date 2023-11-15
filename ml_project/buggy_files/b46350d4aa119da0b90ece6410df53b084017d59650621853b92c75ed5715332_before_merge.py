    def __init__(
        self,
        triples_factory: TriplesFactory,
        minimum_frequency: Optional[float] = None,
        symmetric: bool = True,
        use_tqdm: bool = True,
        use_multiprocessing: bool = False,
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

        if use_multiprocessing:
            use_tqdm = False

        self.candidate_duplicate_relations = get_candidate_duplicate_relations(
            triples_factory=self.triples_factory,
            minimum_frequency=self.minimum_frequency,
            symmetric=symmetric,
            use_tqdm=use_tqdm,
            use_multiprocessing=use_multiprocessing,
        )
        logger.info(
            f'identified {len(self.candidate_duplicate_relations)} candidate duplicate relationships'
            f' at similarity > {self.minimum_frequency} in {self.triples_factory}.',
        )
        self.duplicate_relations_to_delete = {r for r, _ in self.candidate_duplicate_relations}

        self.candidate_inverse_relations = get_candidate_inverse_relations(
            triples_factory=self.triples_factory,
            minimum_frequency=self.minimum_frequency,
            symmetric=symmetric,
            use_tqdm=use_tqdm,
            use_multiprocessing=use_multiprocessing,
        )
        logger.info(
            f'identified {len(self.candidate_inverse_relations)} candidate inverse pairs'
            f' at similarity > {self.minimum_frequency} in {self.triples_factory}',
        )

        if symmetric:
            self.inverses = dict(tuple(sorted(k)) for k in self.candidate_inverse_relations.keys())
            self.inverse_relations_to_delete = set(self.inverses.values())
        else:
            self.mutual_inverse = set()
            self.not_mutual_inverse = set()
            for r1, r2 in self.candidate_inverse_relations:
                if (r2, r1) in self.candidate_inverse_relations:
                    self.mutual_inverse.add((r1, r2))
                else:
                    self.not_mutual_inverse.add((r1, r2))
            logger.info(
                f'{len(self.mutual_inverse)} are mutual inverse ({len(self.mutual_inverse) // 2}'
                f' relations) and {len(self.not_mutual_inverse)} non-mutual inverse.',
            )

            # basically take all candidates
            self.inverses = dict(self.candidate_inverse_relations.keys())
            self.inverse_relations_to_delete = prioritize_mapping(self.candidate_inverse_relations)

        logger.info(f'identified {len(self.inverse_relations_to_delete)} from {self.triples_factory} to delete')