    def _data_to_tensors(self, data: pd.DataFrame) -> Dict[str, torch.Tensor]:
        """
        Convert data to tensors for faster access with :py:meth:`~__getitem__`.

        Args:
            data (pd.DataFrame): preprocessed data

        Returns:
            Dict[str, torch.Tensor]: dictionary of tensors for continous, categorical data, groups, target and
                time index
        """

        index = torch.tensor(data[self._group_ids].to_numpy(np.long), dtype=torch.long)
        time = torch.tensor(data["__time_idx__"].to_numpy(np.long), dtype=torch.long)

        # categorical covariates
        categorical = torch.tensor(data[self.flat_categoricals].to_numpy(np.long), dtype=torch.long)

        # get weight
        if self.weight is not None:
            weight = torch.tensor(
                data["__weight__"].to_numpy(dtype=np.float),
                dtype=torch.float,
            )
        else:
            weight = None

        # get target
        if isinstance(self.target_normalizer, NaNLabelEncoder):
            target = [torch.tensor(data[f"__target__{self.target}"].to_numpy(dtype=np.long), dtype=torch.long)]
        else:
            if len(self.target_names) > 1:
                target = [
                    torch.tensor(
                        data[name].to_numpy(dtype=[np.float, np.long][data[name].dtype.kind in "bi"]),
                        dtype=[torch.float, torch.long][data[name].dtype.kind in "bi"],
                    )
                    for name in self.target_names
                ]
            else:
                target = [torch.tensor(data[f"__target__{self.target}"].to_numpy(dtype=np.float), dtype=torch.float)]

        # continuous covariates
        continuous = torch.tensor(data[self.reals].to_numpy(dtype=np.float), dtype=torch.float)

        tensors = dict(
            reals=continuous, categoricals=categorical, groups=index, target=target, weight=weight, time=time
        )

        return tensors