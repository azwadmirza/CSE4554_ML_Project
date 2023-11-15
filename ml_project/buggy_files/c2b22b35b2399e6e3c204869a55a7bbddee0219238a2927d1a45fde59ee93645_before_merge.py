def main(path: str, directory: str, test_ratios, no_validation: bool, validation_ratios, reload, seed):
    """Make a dataset from the given triples."""
    os.makedirs(directory, exist_ok=True)

    triples_factory = TriplesFactory(path=path)
    ratios = test_ratios if no_validation else validation_ratios

    if seed is None:
        seed = np.random.randint(0, 2 ** 32 - 1)
    sub_triples_factories = triples_factory.split(ratios, random_state=seed)

    for subset_name, subset_tf in zip(LABELS, sub_triples_factories):
        output_path = os.path.join(directory, f'{subset_name}.txt')
        click.echo(f'Outputing {subset_name} to {output_path}')
        np.savetxt(output_path, subset_tf.triples, delimiter='\t', fmt='%s')

    metadata = dict(
        source=os.path.abspath(path),
        ratios=dict(zip(LABELS, ratios)),
        seed=seed,
    )
    with open(os.path.join(directory, 'metadata.json'), 'w') as file:
        json.dump(metadata, file, indent=2)

    if reload:
        if no_validation:
            click.secho('Can not load as dataset if --no-validation was flagged.', fg='red')
            return
        d = PathDataSet(
            training_path=os.path.join(directory, 'train.txt'),
            testing_path=os.path.join(directory, 'test.txt'),
            validation_path=os.path.join(directory, 'valid.txt'),
            eager=True,
        )
        print(d)