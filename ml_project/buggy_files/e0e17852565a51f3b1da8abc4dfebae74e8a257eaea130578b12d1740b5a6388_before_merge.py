    def _merge_with(
        self,
        *others: Union["BaseContainer", Dict[str, Any], List[Any], Tuple[Any], Any],
    ) -> None:
        from .dictconfig import DictConfig
        from .listconfig import ListConfig
        from .omegaconf import OmegaConf

        """merge a list of other Config objects into this one, overriding as needed"""
        for other in others:
            if other is None:
                raise ValueError("Cannot merge with a None config")

            my_flags = {}
            if self._get_flag("allow_objects") is True:
                my_flags = {"allow_objects": True}
            other = _ensure_container(other, flags=my_flags)

            if isinstance(self, DictConfig) and isinstance(other, DictConfig):
                BaseContainer._map_merge(self, other)
            elif isinstance(self, ListConfig) and isinstance(other, ListConfig):
                if self._is_none() or self._is_missing() or self._is_interpolation():
                    self.__dict__["_content"] = []
                else:
                    self.__dict__["_content"].clear()

                if other._is_missing():
                    self._set_value("???")
                elif other._is_none():
                    self._set_value(None)
                else:
                    et = self._metadata.element_type
                    if is_structured_config(et):
                        prototype = OmegaConf.structured(et)
                        for item in other:
                            if isinstance(item, DictConfig):
                                item = OmegaConf.merge(prototype, item)
                            self.append(item)

                    else:
                        for item in other:
                            self.append(item)

                # explicit flags on the source config are replacing the flag values in the destination
                flags = other._metadata.flags
                assert flags is not None
                for flag, value in flags.items():
                    if value is not None:
                        self._set_flag(flag, value)
            else:
                raise TypeError("Cannot merge DictConfig with ListConfig")

        # recursively correct the parent hierarchy after the merge
        self._re_parent()