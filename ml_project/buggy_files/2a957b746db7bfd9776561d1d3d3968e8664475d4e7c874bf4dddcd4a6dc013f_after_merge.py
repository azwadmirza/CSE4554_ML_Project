    def hparams(self, hp: Union[dict, Namespace, Any]):
        hparams_assignment_name = self.__get_hparams_assignment_variable()
        self._hparams_name = hparams_assignment_name
        self._set_hparams(hp)