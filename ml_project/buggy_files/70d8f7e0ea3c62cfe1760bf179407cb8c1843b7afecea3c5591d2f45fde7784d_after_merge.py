    def semantic_analysis_apply_patches(self) -> None:
        patches_by_priority = sorted(self.patches, key=lambda x: x[0])
        for priority, patch_func in patches_by_priority:
            patch_func()