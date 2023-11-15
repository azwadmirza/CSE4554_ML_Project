    def _get_aoe2_base(cls, gamedata):
        """
        Create the aoe2-base modpack.
        """
        modpack = Modpack("aoe2_base")

        mod_def = modpack.get_info()

        mod_def.set_version("1.0c")
        mod_def.set_uid(2000)

        mod_def.add_assets_to_load("data/*")

        cls.organize_nyan_objects(modpack, gamedata)
        cls.organize_media_objects(modpack, gamedata)

        return modpack