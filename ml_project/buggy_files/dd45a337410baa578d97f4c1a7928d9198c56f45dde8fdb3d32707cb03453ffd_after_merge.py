    def get_forked_metrics(self, add_dataloader_idx=False):
        """
        Gets the metrics to log at the end of epoch
        """
        result = {}

        meta = self['meta']
        for k, options in meta.items():
            if k == '_internal':
                continue

            dl_key = self._add_dataloader_idx(k, options["dataloader_idx"], add_dataloader_idx)

            if options['forked']:
                if isinstance(self[k], Metric):
                    result[dl_key] = self[k].compute().detach()
                else:
                    result[dl_key] = self[k]

        return result