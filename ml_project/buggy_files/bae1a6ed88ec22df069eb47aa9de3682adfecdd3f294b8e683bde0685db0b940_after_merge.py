def get_extras_require() -> Dict[str, List[str]]:

    requirements = {
        "checking": ["black", "hacking", "mypy"],
        "codecov": ["codecov", "pytest-cov"],
        "doctest": [
            "cma",
            "pandas",
            "plotly>=4.0.0",
            "scikit-learn>=0.19.0,<0.23.0",
            "scikit-optimize",
            "mlflow",
        ],
        "document": [
            # TODO(hvy): Unpin `sphinx` version after:
            # https://github.com/sphinx-doc/sphinx/issues/8105.
            "sphinx==3.0.4",
            # As reported in: https://github.com/readthedocs/sphinx_rtd_theme/issues/949,
            # `sphinx_rtd_theme` 0.5.0 is still not compatible with `sphinx` >= 3.0.
            "sphinx_rtd_theme<0.5.0",
            "sphinx-gallery",
            "pillow",
            "matplotlib",
            "scikit-learn",
        ],
        "example": [
            "catboost",
            "chainer",
            "lightgbm<3.0.0",
            "mlflow",
            "mpi4py",
            "mxnet",
            "nbval",
            "scikit-image",
            "scikit-learn>=0.19.0,<0.23.0",  # optuna/visualization/param_importances.py.
            "xgboost",
            "keras",
            "tensorflow>=2.0.0",
            "tensorflow-datasets",
        ]
        + (
            (
                ["torch==1.6.0", "torchvision==0.7.0"]
                if sys.platform == "darwin"
                else ["torch==1.6.0+cpu", "torchvision==0.7.0+cpu"]
            )
            + ["pytorch-ignite", "thop"]
            if (3, 5) < sys.version_info[:2]
            else []
        )
        + (["stable-baselines3>=0.7.0"] if (3, 5) < sys.version_info[:2] else [])
        + (
            ["allennlp==1.0.0", "fastai<2", "pytorch_lightning>=0.7.1"]
            if (3, 5) < sys.version_info[:2] < (3, 8)
            else []
        )
        + (["pytorch-lightning>=0.7.2"] if (3, 8) == sys.version_info[:2] else [])
        + (
            ["llvmlite<=0.31.0", "fsspec<0.8.0"] if (3, 5) == sys.version_info[:2] else []
        )  # Newer `llvmlite` is not distributed with wheels for Python 3.5.
        # Newer `fsspec` uses f-strings, which is not compatible with Python 3.5.
        + (["dask[dataframe]", "dask-ml"] if sys.version_info[:2] < (3, 8) else [])
        + (["catalyst"] if (3, 5) < sys.version_info[:2] else []),
        "experimental": ["redis"],
        "testing": [
            # TODO(toshihikoyanase): Remove the version constraint after resolving the issue
            # https://github.com/optuna/optuna/issues/1000.
            "bokeh<2.0.0",
            "chainer>=5.0.0",
            "cma",
            "fakeredis",
            "lightgbm<3.0.0",
            "mlflow",
            "mpi4py",
            "mxnet",
            "pandas",
            "plotly>=4.0.0",
            "pytest",
            "scikit-learn>=0.19.0,<0.23.0",
            "scikit-optimize",
            "xgboost",
            "keras",
            "tensorflow",
            "tensorflow-datasets",
        ]
        + (
            (
                ["torch==1.6.0", "torchvision==0.7.0"]
                if sys.platform == "darwin"
                else ["torch==1.6.0+cpu", "torchvision==0.7.0+cpu"]
            )
            + ["pytorch-ignite"]
            if (3, 5) < sys.version_info[:2]
            else []
        )
        + (
            ["allennlp==1.0.0", "fastai<2", "pytorch_lightning>=0.7.1"]
            if (3, 5) < sys.version_info[:2] < (3, 8)
            else []
        )
        + (["catalyst"] if (3, 5) < sys.version_info[:2] else [])
        + (["pytorch-lightning>=0.7.2"] if (3, 8) == sys.version_info[:2] else []),
        "tests": ["fakeredis", "pytest"],
        "optional": [
            "bokeh<2.0.0",  # optuna/cli.py, optuna/dashboard.py.
            "pandas",  # optuna/study.py
            "plotly>=4.0.0",  # optuna/visualization.
            "redis",  # optuna/storages/redis.py.
            "scikit-learn>=0.19.0,<0.23.0",  # optuna/visualization/param_importances.py.
        ],
        "integration": [
            # TODO(toshihikoyanase): Remove the version constraint after resolving the issue
            # https://github.com/optuna/optuna/issues/1000.
            "chainer>=5.0.0",
            "cma",
            "lightgbm<3.0.0",
            "mlflow",
            "mpi4py",
            "mxnet",
            "pandas",
            "scikit-learn>=0.19.0,<0.23.0",
            "scikit-optimize",
            "xgboost",
            "keras",
            "tensorflow",
            "tensorflow-datasets",
        ]
        + (
            (
                ["torch==1.6.0", "torchvision==0.7.0"]
                if sys.platform == "darwin"
                else ["torch==1.6.0+cpu", "torchvision==0.7.0+cpu"]
            )
            + ["pytorch-ignite"]
            if (3, 5) < sys.version_info[:2]
            else []
        )
        + (
            ["allennlp==1.0.0", "fastai<2", "pytorch-lightning>=0.7.1"]
            if (3, 5) < sys.version_info[:2] < (3, 8)
            else []
        )
        + (["catalyst"] if (3, 5) < sys.version_info[:2] else [])
        + (["pytorch-lightning>=0.7.2"] if (3, 8) == sys.version_info[:2] else []),
    }

    return requirements