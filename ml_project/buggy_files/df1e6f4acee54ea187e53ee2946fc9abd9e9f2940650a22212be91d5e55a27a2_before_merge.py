def get_extras_require():
    # type: () -> Dict[str, List[str]]

    requirements = {
        'checking': [
            'autopep8',
            'hacking',
            'mypy',
        ],
        'codecov': [
            'codecov',
            'pytest-cov',
        ],
        'doctest': [
            'pandas',
            'scikit-learn>=0.19.0',
        ],
        'document': [
            'lightgbm',
            'sphinx',
            'sphinx_rtd_theme',
        ],
        'example': [
            'catboost',
            'chainer',
            'lightgbm',
            'mlflow',
            'mxnet',
            'scikit-image',
            'scikit-learn',
            'xgboost',
        ] + (['fastai<2'] if (3, 5) < sys.version_info[:2] < (3, 8) else [])
        + ([
            'dask[dataframe]',
            'dask-ml',
            'keras',
            'pytorch-ignite',
            'pytorch-lightning',
            # TODO(Yanase): Update examples to support TensorFlow 2.0.
            # See https://github.com/optuna/optuna/issues/565 for further details.
            'tensorflow<2.0.0',
            'torch',
            'torchvision'
        ] if sys.version_info[:2] < (3, 8) else []),
        'testing': [
            'bokeh',
            'chainer>=5.0.0',
            'cma',
            'lightgbm',
            'mock',
            'mpi4py',
            'mxnet',
            'pandas',
            'plotly>=4.0.0',
            'pytest',
            'scikit-learn>=0.19.0',
            'scikit-optimize',
            'xgboost',
        ] + (['fastai<2'] if (3, 5) < sys.version_info[:2] < (3, 8) else [])
        + ([
            'keras',
            'pytorch-ignite',
            'pytorch-lightning',
            'tensorflow',
            'tensorflow-datasets',
            'torch',
            'torchvision'
        ] if sys.version_info[:2] < (3, 8) else []),
    }

    return requirements