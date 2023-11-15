    async def _load(
        self, cog_names: Iterable[str]
    ) -> Tuple[List[str], List[str], List[str], List[str], List[Tuple[str, str]]]:
        """
        Loads cogs by name.
        Parameters
        ----------
        cog_names : list of str

        Returns
        -------
        tuple
            4-tuple of loaded, failed, not found and already loaded cogs.
        """
        failed_packages = []
        loaded_packages = []
        notfound_packages = []
        alreadyloaded_packages = []
        failed_with_reason_packages = []

        bot = self.bot

        cogspecs = []

        for name in cog_names:
            try:
                spec = await bot._cog_mgr.find_cog(name)
                if spec:
                    cogspecs.append((spec, name))
                else:
                    notfound_packages.append(name)
            except Exception as e:
                log.exception("Package import failed", exc_info=e)

                exception_log = "Exception during import of cog\n"
                exception_log += "".join(traceback.format_exception(type(e), e, e.__traceback__))
                bot._last_exception = exception_log
                failed_packages.append(name)

        for spec, name in cogspecs:
            try:
                self._cleanup_and_refresh_modules(spec.name)
                await bot.load_extension(spec)
            except errors.PackageAlreadyLoaded:
                alreadyloaded_packages.append(name)
            except errors.CogLoadError as e:
                failed_with_reason_packages.append((name, str(e)))
            except Exception as e:
                log.exception("Package loading failed", exc_info=e)

                exception_log = "Exception during loading of cog\n"
                exception_log += "".join(traceback.format_exception(type(e), e, e.__traceback__))
                bot._last_exception = exception_log
                failed_packages.append(name)
            else:
                await bot.add_loaded_package(name)
                loaded_packages.append(name)

        return (
            loaded_packages,
            failed_packages,
            notfound_packages,
            alreadyloaded_packages,
            failed_with_reason_packages,
        )