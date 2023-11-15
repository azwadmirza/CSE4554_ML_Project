    def persist(self, model_dir):
        # type: (Text) -> Dict[Text, Any]
        file_name = self.name+".json"
        full_name = os.path.join(model_dir, file_name)
        with io.open(full_name, 'w') as f:
            f.write(str(json.dumps({"dimensions": self.dimensions})))
        return {"ner_duckling_persisted": file_name}