    def create_post(self, path, **kw):
        """Create a new post."""
        self._req_missing_ipynb()
        content = kw.pop('content', None)
        onefile = kw.pop('onefile', False)
        kernel = kw.pop('ipython_kernel', None)
        # is_page is not needed to create the file
        kw.pop('is_page', False)

        metadata = {}
        metadata.update(self.default_metadata)
        metadata.update(kw)

        makedirs(os.path.dirname(path))

        if content.startswith("{"):
            # imported .ipynb file, guaranteed to start with "{" because it’s JSON.
            nb = nbformat.reads(content, current_nbformat)
        else:
            nb = nbformat.v4.new_notebook()
            nb["cells"] = [nbformat.v4.new_markdown_cell(content)]

            if kernelspec is not None:
                if kernel is None:
                    kernel = self.default_kernel
                    self.logger.notice('No kernel specified, assuming "{0}".'.format(kernel))

                IPYNB_KERNELS = {}
                ksm = kernelspec.KernelSpecManager()
                for k in ksm.find_kernel_specs():
                    IPYNB_KERNELS[k] = ksm.get_kernel_spec(k).to_dict()
                    IPYNB_KERNELS[k]['name'] = k
                    del IPYNB_KERNELS[k]['argv']

                if kernel not in IPYNB_KERNELS:
                    self.logger.error('Unknown kernel "{0}". Maybe you mispelled it?'.format(kernel))
                    self.logger.info("Available kernels: {0}".format(", ".join(sorted(IPYNB_KERNELS))))
                    raise Exception('Unknown kernel "{0}"'.format(kernel))

                nb["metadata"]["kernelspec"] = IPYNB_KERNELS[kernel]
            else:
                # Older IPython versions don’t need kernelspecs.
                pass

        if onefile:
            nb["metadata"]["nikola"] = metadata

        with io.open(path, "w+", encoding="utf8") as fd:
            nbformat.write(nb, fd, 4)