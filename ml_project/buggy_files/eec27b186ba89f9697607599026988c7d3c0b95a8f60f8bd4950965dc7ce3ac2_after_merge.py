    def _get_full_key(self, key: Union[DictKeyType, int, slice, None]) -> str:
        from .listconfig import ListConfig
        from .omegaconf import _select_one

        if not isinstance(key, (int, str, Enum, float, bool, slice, type(None))):
            return ""

        def _slice_to_str(x: slice) -> str:
            if x.step is not None:
                return f"{x.start}:{x.stop}:{x.step}"
            else:
                return f"{x.start}:{x.stop}"

        def prepand(full_key: str, parent_type: Any, cur_type: Any, key: Any) -> str:
            if isinstance(key, slice):
                key = _slice_to_str(key)
            elif isinstance(key, Enum):
                key = key.name
            elif isinstance(key, (int, float, bool)):
                key = str(key)

            if issubclass(parent_type, ListConfig):
                if full_key != "":
                    if issubclass(cur_type, ListConfig):
                        full_key = f"[{key}]{full_key}"
                    else:
                        full_key = f"[{key}].{full_key}"
                else:
                    full_key = f"[{key}]"
            else:
                if full_key == "":
                    full_key = key
                else:
                    if issubclass(cur_type, ListConfig):
                        full_key = f"{key}{full_key}"
                    else:
                        full_key = f"{key}.{full_key}"
            return full_key

        if key is not None and key != "":
            assert isinstance(self, Container)
            cur, _ = _select_one(
                c=self, key=str(key), throw_on_missing=False, throw_on_type_error=False
            )
            if cur is None:
                cur = self
                full_key = prepand("", type(cur), None, key)
                if cur._key() is not None:
                    full_key = prepand(
                        full_key, type(cur._get_parent()), type(cur), cur._key()
                    )
            else:
                full_key = prepand("", type(cur._get_parent()), type(cur), cur._key())
        else:
            cur = self
            if cur._key() is None:
                return ""
            full_key = self._key()

        assert cur is not None
        while cur._get_parent() is not None:
            cur = cur._get_parent()
            assert cur is not None
            key = cur._key()
            if key is not None:
                full_key = prepand(
                    full_key, type(cur._get_parent()), type(cur), cur._key()
                )

        return full_key