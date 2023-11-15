    def save_slp(path, target, palette=None):
        """
        save a slp as png.
        """
        from .texture import Texture
        from .slp import SLP
        from .driver import get_palette

        if not palette:
            palette = get_palette(data, game_versions)

        with path.open("rb") as slpfile:
            tex = Texture(SLP(slpfile.read()), palette)

            out_path, filename = os.path.split(target)
            tex.save(Directory(out_path).root, filename)