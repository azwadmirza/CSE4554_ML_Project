    def load_config(
        self,
        config_path: str,
        is_primary_config: bool,
        package_override: Optional[str] = None,
    ) -> ConfigResult:
        normalized_config_path = self._normalize_file_name(config_path)
        res = importlib_resources.files(self.path).joinpath(normalized_config_path)
        if not res.exists():
            raise ConfigLoadError(f"Config not found : {normalized_config_path}")

        with res.open() as f:
            header_text = f.read(512)
            header = ConfigSource._get_header_dict(header_text)
            self._update_package_in_header(
                header=header,
                normalized_config_path=normalized_config_path,
                is_primary_config=is_primary_config,
                package_override=package_override,
            )
            f.seek(0)
            cfg = OmegaConf.load(f)
            return ConfigResult(
                config=self._embed_config(cfg, header["package"]),
                path=f"{self.scheme()}://{self.path}",
                provider=self.provider,
                header=header,
            )