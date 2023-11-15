    def _get_aoe1_base(cls, gamedata):
        """
        Create the aoe1-base modpack.
        """
        modpack = Modpack("aoe1-base")

        mod_def = modpack.get_info()

        mod_def.set_version("1.0B")
        mod_def.set_uid(1000)

        mod_def.add_assets_to_load("data/*")

        AoCModpackSubprocessor.organize_nyan_objects(modpack, gamedata)
        AoCModpackSubprocessor.organize_media_objects(modpack, gamedata)

        return modpack