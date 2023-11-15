def _main():
    """Test unleaking FB15K.

    Run with ``python -m pykeen.triples.leakage``.
    """
    from pykeen.datasets import get_dataset
    logging.basicConfig(format='pykeen: %(message)s', level=logging.INFO)

    fb15k = get_dataset(dataset='fb15k')
    fb15k.summarize()

    n = 401  # magic 401 from the paper
    train, test, validate = unleak(fb15k.training, fb15k.testing, fb15k.validation, n=n)
    print()
    EagerDataset(train, test, validate).summarize(title='FB15k (cleaned)')

    fb15k237 = get_dataset(dataset='fb15k237')
    print('\nSummary FB15K-237')
    fb15k237.summarize()