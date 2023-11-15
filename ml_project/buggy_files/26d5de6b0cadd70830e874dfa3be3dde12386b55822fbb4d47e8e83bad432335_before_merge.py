    def write_labels(self, labels: Union[List[dict], List[Label]], index: Optional[str] = None):
        index = index or self.label_index
        label_objects = [Label.from_dict(l) if isinstance(l, dict) else l for l in labels]

        for label in label_objects:
            label_id = uuid.uuid4()
            self.indexes[index][label_id] = label