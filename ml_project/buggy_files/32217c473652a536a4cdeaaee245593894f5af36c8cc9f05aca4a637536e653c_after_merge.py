    def load(
        cls,
        dir_path: str,
        adata: Optional[AnnData] = None,
        use_cuda: bool = False,
    ):
        """
        Instantiate a model from the saved output.

        Parameters
        ----------
        dir_path
            Path to saved outputs.
        adata
            AnnData organized in the same way as data used to train model.
            It is not necessary to run :func:`~scvi.data.setup_anndata`,
            as AnnData is validated against the saved `scvi` setup dictionary.
            If None, will check for and load anndata saved with the model.
        use_cuda
            Whether to load model on GPU.

        Returns
        -------
        Model with loaded state dictionaries.

        Examples
        --------
        >>> vae = SCVI.load(adata, save_path)
        >>> vae.get_latent_representation()
        """
        model_path = os.path.join(dir_path, "model_params.pt")
        setup_dict_path = os.path.join(dir_path, "attr.pkl")
        adata_path = os.path.join(dir_path, "adata.h5ad")
        varnames_path = os.path.join(dir_path, "var_names.csv")

        if os.path.exists(adata_path) and adata is None:
            adata = read(adata_path)
        elif not os.path.exists(adata_path) and adata is None:
            raise ValueError(
                "Save path contains no saved anndata and no adata was passed."
            )
        var_names = np.genfromtxt(varnames_path, delimiter=",", dtype=str)
        user_var_names = adata.var_names.astype(str)
        if not np.array_equal(var_names, user_var_names):
            logger.warning(
                "var_names for adata passed in does not match var_names of "
                "adata used to train the model. For valid results, the vars "
                "need to be the same and in the same order as the adata used to train the model."
            )

        with open(setup_dict_path, "rb") as handle:
            attr_dict = pickle.load(handle)

        scvi_setup_dict = attr_dict.pop("scvi_setup_dict_")

        transfer_anndata_setup(scvi_setup_dict, adata)

        if "init_params_" not in attr_dict.keys():
            raise ValueError(
                "No init_params_ were saved by the model. Check out the "
                "developers guide if creating custom models."
            )
        # get the parameters for the class init signiture
        init_params = attr_dict.pop("init_params_")

        # update use_cuda from the saved model
        use_cuda = use_cuda and torch.cuda.is_available()
        init_params["use_cuda"] = use_cuda

        # grab all the parameters execept for kwargs (is a dict)
        non_kwargs = {k: v for k, v in init_params.items() if not isinstance(v, dict)}
        # expand out kwargs
        kwargs = {k: v for k, v in init_params.items() if isinstance(v, dict)}
        kwargs = {k: v for (i, j) in kwargs.items() for (k, v) in j.items()}
        model = cls(adata, **non_kwargs, **kwargs)
        for attr, val in attr_dict.items():
            setattr(model, attr, val)

        if use_cuda:
            model.model.load_state_dict(torch.load(model_path))
            model.model.cuda()
        else:
            device = torch.device("cpu")
            model.model.load_state_dict(torch.load(model_path, map_location=device))

        model.model.eval()
        model._validate_anndata(adata)

        return model