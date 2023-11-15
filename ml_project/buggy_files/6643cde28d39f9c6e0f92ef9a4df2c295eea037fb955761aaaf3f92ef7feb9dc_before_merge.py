    def parse_raw(self) -> None:
        raw_obj: Dict[str, Any] = json.loads(self.text)  # type: ignore
        obj_name = raw_obj.get('title', 'Model')
        self.parse_raw_obj(obj_name, raw_obj)