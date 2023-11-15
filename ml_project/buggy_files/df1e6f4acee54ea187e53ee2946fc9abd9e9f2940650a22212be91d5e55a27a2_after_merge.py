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
            # TODO(Yanase): Update sklearn integration to support v0.22.1 or newer.
            # See https://github.com/optuna/optuna/issues/825 for further details.
            'scikit-learn>=0.19.0,<=0.22.0',
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
            # TODO(Yanase): Update sklearn integration to support v0.22.1 or newer.
            # See https://github.com/optuna/optuna/issues/825 for further details.
            'scikit-learn<=0.22.0',
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
            # TODO(Yanase): Update sklearn integration to support v0.22.1 or newer.
            # See https://github.com/optuna/optuna/issues/825 for further details.
            'scikit-learn>=0.19.0,<=0.22.0',
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