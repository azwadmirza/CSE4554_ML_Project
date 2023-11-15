    def _get_swgb_base(cls, gamedata):
        """
        Create the swgb-base modpack.
        """
        modpack = Modpack("swgb-base")

        mod_def = modpack.get_info()

        mod_def.set_version("GOG")
        mod_def.set_uid(5000)

        mod_def.add_assets_to_load("data/*")

        AoCModpackSubprocessor.organize_nyan_objects(modpack, gamedata)
        AoCModpackSubprocessor.organize_media_objects(modpack, gamedata)

        return modpack