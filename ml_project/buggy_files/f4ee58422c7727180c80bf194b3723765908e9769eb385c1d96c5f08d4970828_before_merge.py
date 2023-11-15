    def get_subjects_iterable(self) -> Iterator:
        # I need a DataLoader to handle parallelism
        # But this loader is always expected to yield single subject samples
        self._print(
            '\nCreating subjects loader with', self.num_workers, 'workers')
        subjects_loader = DataLoader(
            self.subjects_dataset,
            num_workers=self.num_workers,
            collate_fn=lambda x: x[0],
            shuffle=self.shuffle_subjects,
        )
        return iter(subjects_loader)