    def _install(self, args):
        """
        Install a package from a repo
        """
        if len(args) < 2:
            raise SPMInvocationError("A package must be specified")

        caller_opts = self.opts.copy()
        caller_opts["file_client"] = "local"
        self.caller = salt.client.Caller(mopts=caller_opts)
        self.client = salt.client.get_local_client(self.opts["conf_file"])
        cache = salt.cache.Cache(self.opts)

        packages = args[1:]
        file_map = {}
        optional = []
        recommended = []
        to_install = []
        for pkg in packages:
            if pkg.endswith(".spm"):
                if self._pkgfiles_fun("path_exists", pkg):
                    comps = pkg.split("-")
                    comps = os.path.split("-".join(comps[:-2]))
                    pkg_name = comps[-1]

                    formula_tar = tarfile.open(pkg, "r:bz2")
                    formula_ref = formula_tar.extractfile(
                        "{0}/FORMULA".format(pkg_name)
                    )
                    formula_def = salt.utils.yaml.safe_load(formula_ref)

                    file_map[pkg_name] = pkg
                    to_, op_, re_ = self._check_all_deps(
                        pkg_name=pkg_name, pkg_file=pkg, formula_def=formula_def
                    )
                    to_install.extend(to_)
                    optional.extend(op_)
                    recommended.extend(re_)
                    formula_tar.close()
                else:
                    raise SPMInvocationError("Package file {0} not found".format(pkg))
            else:
                to_, op_, re_ = self._check_all_deps(pkg_name=pkg)
                to_install.extend(to_)
                optional.extend(op_)
                recommended.extend(re_)

        optional = set(filter(len, optional))
        if optional:
            self.ui.status(
                "The following dependencies are optional:\n\t{0}\n".format(
                    "\n\t".join(optional)
                )
            )
        recommended = set(filter(len, recommended))
        if recommended:
            self.ui.status(
                "The following dependencies are recommended:\n\t{0}\n".format(
                    "\n\t".join(recommended)
                )
            )

        to_install = set(filter(len, to_install))
        msg = "Installing packages:\n\t{0}\n".format("\n\t".join(to_install))
        if not self.opts["assume_yes"]:
            self.ui.confirm(msg)

        repo_metadata = self._get_repo_metadata()

        dl_list = {}
        for package in to_install:
            if package in file_map:
                self._install_indv_pkg(package, file_map[package])
            else:
                for repo in repo_metadata:
                    repo_info = repo_metadata[repo]
                    if package in repo_info["packages"]:
                        dl_package = False
                        repo_ver = repo_info["packages"][package]["info"]["version"]
                        repo_rel = repo_info["packages"][package]["info"]["release"]
                        repo_url = repo_info["info"]["url"]
                        if package in dl_list:
                            # Check package version, replace if newer version
                            if repo_ver == dl_list[package]["version"]:
                                # Version is the same, check release
                                if repo_rel > dl_list[package]["release"]:
                                    dl_package = True
                                elif repo_rel == dl_list[package]["release"]:
                                    # Version and release are the same, give
                                    # preference to local (file://) repos
                                    if dl_list[package]["source"].startswith("file://"):
                                        if not repo_url.startswith("file://"):
                                            dl_package = True
                            elif repo_ver > dl_list[package]["version"]:
                                dl_package = True
                        else:
                            dl_package = True

                        if dl_package is True:
                            # Put together download directory
                            cache_path = os.path.join(self.opts["spm_cache_dir"], repo)

                            # Put together download paths
                            dl_url = "{0}/{1}".format(
                                repo_info["info"]["url"],
                                repo_info["packages"][package]["filename"],
                            )
                            out_file = os.path.join(
                                cache_path, repo_info["packages"][package]["filename"]
                            )
                            dl_list[package] = {
                                "version": repo_ver,
                                "release": repo_rel,
                                "source": dl_url,
                                "dest_dir": cache_path,
                                "dest_file": out_file,
                            }

        for package in dl_list:
            dl_url = dl_list[package]["source"]
            cache_path = dl_list[package]["dest_dir"]
            out_file = dl_list[package]["dest_file"]

            # Make sure download directory exists
            if not os.path.exists(cache_path):
                os.makedirs(cache_path)

            # Download the package
            if dl_url.startswith("file://"):
                dl_url = dl_url.replace("file://", "")
                shutil.copyfile(dl_url, out_file)
            else:
                with salt.utils.files.fopen(out_file, "wb") as outf:
                    outf.write(
                        self._query_http(dl_url, repo_info["info"], decode_body=False)
                    )

        # First we download everything, then we install
        for package in dl_list:
            out_file = dl_list[package]["dest_file"]
            # Kick off the install
            self._install_indv_pkg(package, out_file)
        return