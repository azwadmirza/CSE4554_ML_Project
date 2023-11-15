    def _data_to_tensors(self, data: pd.DataFrame) -> Dict[str, torch.Tensor]:
        """
        Convert data to tensors for faster access with :py:meth:`~__getitem__`.

        Args:
            data (pd.DataFrame): preprocessed data

        Returns:
            Dict[str, torch.Tensor]: dictionary of tensors for continous, categorical data, groups, target and
                time index
        """

        index = check_for_nonfinite(
            torch.tensor(data[self._group_ids].to_numpy(np.long), dtype=torch.long), self.group_ids
        )
        time = check_for_nonfinite(
            torch.tensor(data["__time_idx__"].to_numpy(np.long), dtype=torch.long), self.time_idx
        )

        # categorical covariates
        categorical = check_for_nonfinite(
            torch.tensor(data[self.flat_categoricals].to_numpy(np.long), dtype=torch.long), self.flat_categoricals
        )

        # get weight
        if self.weight is not None:
            weight = check_for_nonfinite(
                torch.tensor(
                    data["__weight__"].to_numpy(dtype=np.float),
                    dtype=torch.float,
                ),
                self.weight,
            )
        else:
            weight = None

        # get target
        if isinstance(self.target_normalizer, NaNLabelEncoder):
            target = [
                check_for_nonfinite(
                    torch.tensor(data[f"__target__{self.target}"].to_numpy(dtype=np.long), dtype=torch.long),
                    self.target,
                )
            ]
        else:
            if not isinstance(self.target, str):  # multi-target
                target = [
                    check_for_nonfinite(
                        torch.tensor(
                            data[f"__target__{name}"].to_numpy(
                                dtype=[np.float, np.long][data[name].dtype.kind in "bi"]
                            ),
                            dtype=[torch.float, torch.long][data[name].dtype.kind in "bi"],
                        ),
                        name,
                    )
                    for name in self.target_names
                ]
            else:
                target = [
                    check_for_nonfinite(
                        torch.tensor(data[f"__target__{self.target}"].to_numpy(dtype=np.float), dtype=torch.float),
                        self.target,
                    )
                ]

        # continuous covariates
        continuous = check_for_nonfinite(
            torch.tensor(data[self.reals].to_numpy(dtype=np.float), dtype=torch.float), self.reals
        )

        tensors = dict(
            reals=continuous, categoricals=categorical, groups=index, target=target, weight=weight, time=time
        )

        return tensors