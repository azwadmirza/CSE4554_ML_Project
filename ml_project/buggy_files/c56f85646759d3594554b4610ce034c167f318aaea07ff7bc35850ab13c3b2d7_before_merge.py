    def _calculate_hashes(self, file_infos):
        file_infos = list(file_infos)
        with Tqdm(
            total=len(file_infos),
            unit="md5",
            desc="Computing file/dir hashes (only done once)",
        ) as pbar:
            worker = pbar.wrap_fn(self.get_file_hash)
            with ThreadPoolExecutor(max_workers=self.hash_jobs) as executor:
                hashes = (
                    value for typ, value in executor.map(worker, file_infos)
                )
                return dict(zip(file_infos, hashes))