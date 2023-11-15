    def toggle_dxvk(self, enable, version=None, dxvk_manager: dxvk.DXVKManager = None):
        # manual version only sets the dlls to native
        if version.lower() != "manual":
            if enable:
                if not dxvk_manager.is_available():
                    dxvk_manager.download()
                dxvk_manager.enable()
            else:
                dxvk_manager.disable()

        if enable:
            for dll in dxvk_manager.dxvk_dlls:
                # We have to make sure that the dll exists before setting it to native
                if dxvk_manager.dxvk_dll_exists(dll):
                    self.dll_overrides[dll] = "n"