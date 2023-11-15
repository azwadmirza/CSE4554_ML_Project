    async def subfolders_in_tree(self):
        return_folders = []
        async for f in self.multirglob("", folder=True):
            with contextlib.suppress(ValueError):
                if (
                    f not in return_folders
                    and f.is_dir()
                    and f.path != self.localtrack_folder
                    and f.path.relative_to(self.path)
                ):
                    return_folders.append(f)
        return sorted(return_folders, key=lambda x: x.to_string_user().lower())