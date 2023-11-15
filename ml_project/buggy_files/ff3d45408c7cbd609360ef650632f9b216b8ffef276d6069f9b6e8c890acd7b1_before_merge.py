    def get_subjects_iterable(self) -> Iterator:
        # I need a DataLoader to handle parallelism
        # But this loader is always expected to yield single subject samples
        self._print(
            f'\nCreating subjects loader with {self.num_workers} workers')
        subjects_loader = DataLoader(
            self.subjects_dataset,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
            batch_size=1,
            collate_fn=self.get_first_item,
            shuffle=self.shuffle_subjects,
        )
        return iter(subjects_loader)