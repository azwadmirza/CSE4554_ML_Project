        def create_virtual_dataset(self, name, layout, fillvalue=None):
            """Create a new virtual dataset in this group.

            See virtual datasets in the docs for more information.

            name
                (str) Name of the new dataset

            layout
                (VirtualLayout) Defines the sources for the virtual dataset

            fillvalue
                The value to use where there is no data.

            """
            from .vds import VDSmap
            # Encode filenames and dataset names appropriately.
            sources = []
            for vspace, file_name, dset_name, src_space in layout.sources:
                if file_name == self.file.filename:
                    # use relative path if the source dataset is in the same
                    # file, in order to keep the virtual dataset valid in case
                    # the file is renamed.
                    file_name = '.'
                sources.append(VDSmap(vspace, filename_encode(file_name),
                                      self._e(dset_name), src_space))

            with phil:
                group = self

                if name:
                    if '/' in name:
                        h5objects = [obj for obj in name.split('/') if len(obj)]
                        name = h5objects[-1]
                        h5objects = h5objects[:-1]

                        for new_group in h5objects:
                            group = group.get(new_group) or group.create_group(new_group)

                    name = self._e(name)

                dsid = dataset.make_new_virtual_dset(group, layout.shape,
                         sources=sources, dtype=layout.dtype, name=name,
                         maxshape=layout.maxshape, fillvalue=fillvalue)

                dset = dataset.Dataset(dsid)

            return dset