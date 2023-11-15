    def setRestartTyp(self,starttyp):
        self.restart = starttyp
        # ToDo: Somehow caused by circular import under python3 refactor
        web.py3_restart_Typ = starttyp