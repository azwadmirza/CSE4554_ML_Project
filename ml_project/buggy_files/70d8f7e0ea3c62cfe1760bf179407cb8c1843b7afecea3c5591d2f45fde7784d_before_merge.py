    def semantic_analysis_apply_patches(self) -> None:
        for patch_func in self.patches:
            patch_func()