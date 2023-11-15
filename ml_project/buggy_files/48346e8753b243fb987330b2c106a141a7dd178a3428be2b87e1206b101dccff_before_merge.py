    def _preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Scale continuous variables, encode categories and set aside target and weight.

        Args:
            data (pd.DataFrame): original data

        Returns:
            pd.DataFrame: pre-processed dataframe
        """
        # encode group ids - this encoding
        for name, group_name in self._group_ids_mapping.items():
            self.categorical_encoders[group_name] = NaNLabelEncoder().fit(data[name].to_numpy().reshape(-1))
            data[group_name] = self.transform_values(name, data[name], inverse=False, group_id=True)

        # encode categoricals
        if isinstance(
            self.target_normalizer, (GroupNormalizer, MultiNormalizer)
        ):  # if we use a group normalizer, group_ids must be encoded as well
            group_ids_to_encode = self.group_ids
        else:
            group_ids_to_encode = []
        for name in set(group_ids_to_encode + self.categoricals):
            allow_nans = name in self.dropout_categoricals
            if name in self.variable_groups:  # fit groups
                columns = self.variable_groups[name]
                if name not in self.categorical_encoders:
                    self.categorical_encoders[name] = NaNLabelEncoder(add_nan=allow_nans).fit(
                        data[columns].to_numpy().reshape(-1)
                    )
                elif self.categorical_encoders[name] is not None:
                    try:
                        check_is_fitted(self.categorical_encoders[name])
                    except NotFittedError:
                        self.categorical_encoders[name] = self.categorical_encoders[name].fit(
                            data[columns].to_numpy().reshape(-1)
                        )
            else:
                if name not in self.categorical_encoders:
                    self.categorical_encoders[name] = NaNLabelEncoder(add_nan=allow_nans).fit(data[name])
                elif self.categorical_encoders[name] is not None and name not in self.target_names:
                    try:
                        check_is_fitted(self.categorical_encoders[name])
                    except NotFittedError:
                        self.categorical_encoders[name] = self.categorical_encoders[name].fit(data[name])

        # encode them
        for name in set(group_ids_to_encode + self.flat_categoricals):
            if name not in self.target_names:
                data[name] = self.transform_values(name, data[name], inverse=False)

        # save special variables
        assert "__time_idx__" not in data.columns, "__time_idx__ is a protected column and must not be present in data"
        data["__time_idx__"] = data[self.time_idx]  # save unscaled
        for target in self.target_names:
            assert (
                f"__target__{target}" not in data.columns
            ), f"__target__{target} is a protected column and must not be present in data"
            data[f"__target__{target}"] = data[target]
        if self.weight is not None:
            data["__weight__"] = data[self.weight]

        # train target normalizer
        if self.target_normalizer is not None:

            # fit target normalizer
            try:
                check_is_fitted(self.target_normalizer)
            except NotFittedError:
                if isinstance(self.target_normalizer, EncoderNormalizer):
                    self.target_normalizer.fit(data[self.target])
                elif isinstance(self.target_normalizer, (GroupNormalizer, MultiNormalizer)):
                    self.target_normalizer.fit(data[self.target], data)
                else:
                    self.target_normalizer.fit(data[self.target])

            # transform target
            if isinstance(self.target_normalizer, EncoderNormalizer):
                # we approximate the scales and target transformation by assuming one
                # transformation over the entire time range but by each group
                common_init_args = [
                    name
                    for name in inspect.signature(GroupNormalizer.__init__).parameters.keys()
                    if name in inspect.signature(EncoderNormalizer.__init__).parameters.keys()
                    and name not in ["data", "self"]
                ]
                copy_kwargs = {name: getattr(self.target_normalizer, name) for name in common_init_args}
                normalizer = GroupNormalizer(groups=self.group_ids, **copy_kwargs)
                data[self.target], scales = normalizer.fit_transform(data[self.target], data, return_norm=True)
            elif isinstance(self.target_normalizer, GroupNormalizer):
                data[self.target], scales = self.target_normalizer.transform(data[self.target], data, return_norm=True)
            elif isinstance(self.target_normalizer, MultiNormalizer):
                transformed, scales = self.target_normalizer.transform(data[self.target], data, return_norm=True)
                for idx, target in enumerate(self.target_names):
                    data[target] = transformed[idx]
            elif isinstance(self.target_normalizer, NaNLabelEncoder):
                data[self.target] = self.target_normalizer.transform(data[self.target])
                data[f"__target__{self.target}"] = data[
                    self.target
                ]  # overwrite target because it requires encoding (continuous targets should not be normalized)
                scales = None
            else:
                data[self.target], scales = self.target_normalizer.transform(data[self.target], return_norm=True)

            # add target scales
            if self.add_target_scales:
                if not isinstance(self.target_normalizer, MultiNormalizer):
                    scales = [scales]
                for target_idx, target in enumerate(self.target_names):
                    if not isinstance(self.target_normalizers[target_idx], NaNLabelEncoder):
                        for scale_idx, name in enumerate(["center", "scale"]):
                            feature_name = f"{target}_{name}"
                            assert (
                                feature_name not in data.columns
                            ), f"{feature_name} is a protected column and must not be present in data"
                            data[feature_name] = scales[target_idx][:, scale_idx].squeeze()
                            if feature_name not in self.reals:
                                self.static_reals.append(feature_name)
        # rescale continuous variables apart from target
        for name in self.reals:
            if name in self.target_names:
                continue
            if name not in self.scalers:
                self.scalers[name] = StandardScaler().fit(data[[name]])
            elif self.scalers[name] is not None:
                try:
                    check_is_fitted(self.scalers[name])
                except NotFittedError:
                    if isinstance(self.scalers[name], GroupNormalizer):
                        self.scalers[name] = self.scalers[name].fit(data[[name]], data)
                    else:
                        self.scalers[name] = self.scalers[name].fit(data[[name]])
            if self.scalers[name] is not None and not isinstance(self.scalers[name], EncoderNormalizer):
                data[name] = self.transform_values(name, data[name], data=data, inverse=False)

        # encode constant values
        self.encoded_constant_fill_strategy = {}
        for name, value in self.constant_fill_strategy.items():
            if name in self.target_names:
                self.encoded_constant_fill_strategy[f"__target__{name}"] = value
            self.encoded_constant_fill_strategy[name] = self.transform_values(
                name, np.array([value]), data=data, inverse=False
            )[0]
        return data