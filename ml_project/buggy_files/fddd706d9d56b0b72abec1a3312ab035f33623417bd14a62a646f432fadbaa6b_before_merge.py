def _main():
    """Test unleaking FB15K.

    Run with ``python -m pykeen.triples.leakage``.
    """
    from pykeen.datasets import get_dataset
    logging.basicConfig(format='pykeen: %(message)s', level=logging.INFO)

    print('Summary FB15K')
    fb15k = get_dataset(dataset='fb15k')
    summarize(fb15k.training, fb15k.testing, fb15k.validation)

    print('\nSummary FB15K (cleaned)')
    n = 401  # magic 401 from the paper
    train, test, validate = unleak(fb15k.training, fb15k.testing, fb15k.validation, n=n)
    summarize(train, test, validate)

    print('\nSummary FB15K-237')
    fb15k237 = get_dataset(dataset='fb15k237')
    summarize(fb15k237.training, fb15k237.testing, fb15k237.validation)