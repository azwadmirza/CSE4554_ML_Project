def _download(url: str, path: Path):
    from tqdm.auto import tqdm
    from urllib.request import urlretrieve

    path.parent.mkdir(parents=True, exist_ok=True)
    with tqdm(unit='B', unit_scale=True, miniters=1, desc=path.name) as t:

        def update_to(b=1, bsize=1, tsize=None):
            if tsize is not None:
                t.total = tsize
            t.update(b * bsize - t.n)

        try:
            urlretrieve(url, str(path), reporthook=update_to)
        except Exception:
            # Make sure file doesn’t exist half-downloaded
            if path.is_file():
                path.unlink()
            raise