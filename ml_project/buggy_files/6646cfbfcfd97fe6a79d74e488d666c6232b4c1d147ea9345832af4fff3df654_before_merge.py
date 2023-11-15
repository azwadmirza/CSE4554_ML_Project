    def __init__(
        self,
        *,
        path: Union[None, str, TextIO] = None,
        triples: Optional[LabeledTriples] = None,
        path_to_numeric_triples: Union[None, str, TextIO] = None,
        numeric_triples: Optional[np.ndarray] = None,
        **kwargs,
    ) -> None:
        """Initialize the multi-modal triples factory.

        :param path: The path to a 3-column TSV file with triples in it. If not specified,
         you should specify ``triples``.
        :param triples:  A 3-column numpy array with triples in it. If not specified,
         you should specify ``path``
        :param path_to_numeric_triples: The path to a 3-column TSV file with triples and
         numeric. If not specified, you should specify ``numeric_triples``.
        :param numeric_triples:  A 3-column numpy array with numeric triples in it. If not
         specified, you should specify ``path_to_numeric_triples``.
        """
        if path is None:
            base = TriplesFactory.from_labeled_triples(triples=triples, **kwargs)
        else:
            base = TriplesFactory.from_path(path=path, **kwargs)
        super().__init__(
            entity_to_id=base.entity_to_id,
            relation_to_id=base.relation_to_id,
            _triples=base.triples,
            mapped_triples=base.mapped_triples,
            relation_to_inverse=base.relation_to_inverse,
        )

        if path_to_numeric_triples is None and numeric_triples is None:
            raise ValueError('Must specify one of path_to_numeric_triples or numeric_triples')
        elif path_to_numeric_triples is not None and numeric_triples is not None:
            raise ValueError('Must not specify both path_to_numeric_triples and numeric_triples')
        elif path_to_numeric_triples is not None:
            numeric_triples = load_triples(path_to_numeric_triples)

        self.numeric_literals, self.literals_to_id = create_matrix_of_literals(
            numeric_triples=numeric_triples,
            entity_to_id=self.entity_to_id,
        )