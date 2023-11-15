    def create_handler(self, window: Union[ElectrumWindow, InstallWizard]) -> 'QtHandlerBase':
        raise NotImplementedError()