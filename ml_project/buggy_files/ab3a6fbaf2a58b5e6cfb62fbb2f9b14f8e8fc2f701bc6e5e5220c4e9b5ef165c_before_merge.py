def unleak(
    train: TriplesFactory,
    *triples_factories: TriplesFactory,
    n: Union[None, int, float] = None,
    minimum_frequency: Optional[float] = None,
) -> Iterable[TriplesFactory]:
    """Unleak a train, test, and validate triples factory.

    :param train: The target triples factory
    :param triples_factories: All other triples factories (test, validate, etc.)
    :param n: Either the (integer) number of top relations to keep or the (float) percentage of top relationships
     to keep. If left none, frequent relations are not removed.
    :param minimum_frequency: The minimum overlap between two relations' triples to consider them as inverses or
     duplicates. The default value, 0.97, is taken from
     `Toutanova and Chen (2015) <https://www.aclweb.org/anthology/W15-4007/>`_, who originally described the generation
     of FB15k-237.
    """
    if n is not None:
        frequent_relations = train.get_most_frequent_relations(n=n)
        logger.info(f'keeping most frequent relations from {train}')
        train = train.new_with_relations(frequent_relations)
        triples_factories = [
            triples_factory.new_with_relations(frequent_relations)
            for triples_factory in triples_factories
        ]

    # Calculate which relations are the inverse ones
    sealant = Sealant(train, minimum_frequency=minimum_frequency)

    if not sealant.relations_to_delete:
        logger.info(f'no relations to delete identified from {train}')
    else:
        train = sealant.apply(train)
        triples_factories = [
            sealant.apply(triples_factory)
            for triples_factory in triples_factories
        ]

    return reindex(train, *triples_factories)