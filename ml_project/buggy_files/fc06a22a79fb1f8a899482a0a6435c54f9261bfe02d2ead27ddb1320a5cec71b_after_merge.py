    def load(
        cls,
        dir_path: str,
        adata_seq: Optional[AnnData] = None,
        adata_spatial: Optional[AnnData] = None,
        use_cuda: bool = False,
    ):
        """
        Instantiate a model from the saved output.

        Parameters
        ----------
        adata_seq
            AnnData organized in the same way as data used to train model.
            It is not necessary to run :func:`~scvi.data.setup_anndata`,
            as AnnData is validated against the saved `scvi` setup dictionary.
            AnnData must be registered via :func:`~scvi.data.setup_anndata`.
        adata_spatial
            AnnData organized in the same way as data used to train model.
            If None, will check for and load anndata saved with the model.
        dir_path
            Path to saved outputs.
        use_cuda
            Whether to load model on GPU.

        Returns
        -------
        Model with loaded state dictionaries.

        Examples
        --------
        >>> vae = GIMVI.load(adata_seq, adata_spatial, save_path)
        >>> vae.get_latent_representation()
        """
        model_path = os.path.join(dir_path, "model_params.pt")
        setup_dict_path = os.path.join(dir_path, "attr.pkl")
        seq_data_path = os.path.join(dir_path, "adata_seq.h5ad")
        spatial_data_path = os.path.join(dir_path, "adata_spatial.h5ad")
        seq_var_names_path = os.path.join(dir_path, "var_names_seq.csv")
        spatial_var_names_path = os.path.join(dir_path, "var_names_spatial.csv")

        if adata_seq is None and os.path.exists(seq_data_path):
            adata_seq = read(seq_data_path)
        elif adata_seq is None and not os.path.exists(seq_data_path):
            raise ValueError(
                "Save path contains no saved anndata and no adata was passed."
            )
        if adata_spatial is None and os.path.exists(spatial_data_path):
            adata_spatial = read(spatial_data_path)
        elif adata_spatial is None and not os.path.exists(spatial_data_path):
            raise ValueError(
                "Save path contains no saved anndata and no adata was passed."
            )
        adatas = [adata_seq, adata_spatial]

        seq_var_names = np.genfromtxt(seq_var_names_path, delimiter=",", dtype=str)
        spatial_var_names = np.genfromtxt(
            spatial_var_names_path, delimiter=",", dtype=str
        )
        var_names = [seq_var_names, spatial_var_names]

        for i, adata in enumerate(adatas):
            saved_var_names = var_names[i]
            user_var_names = adata.var_names.astype(str)
            if not np.array_equal(saved_var_names, user_var_names):
                logger.warning(
                    "var_names for adata passed in does not match var_names of "
                    "adata used to train the model. For valid results, the vars "
                    "need to be the same and in the same order as the adata used to train the model."
                )

        with open(setup_dict_path, "rb") as handle:
            attr_dict = pickle.load(handle)

        scvi_setup_dicts = attr_dict.pop("scvi_setup_dicts_")
        transfer_anndata_setup(scvi_setup_dicts["seq"], adata_seq)
        transfer_anndata_setup(scvi_setup_dicts["spatial"], adata_spatial)

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
        model = cls(adata_seq, adata_spatial, **non_kwargs, **kwargs)
        for attr, val in attr_dict.items():
            setattr(model, attr, val)

        if use_cuda:
            model.model.load_state_dict(torch.load(model_path))
            model.model.cuda()
        else:
            device = torch.device("cpu")
            model.model.load_state_dict(torch.load(model_path, map_location=device))
        model.model.eval()
        return model