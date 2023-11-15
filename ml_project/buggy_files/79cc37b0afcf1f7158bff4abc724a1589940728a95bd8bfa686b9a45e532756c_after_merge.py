def find_one_filetype(path: Path, filename: str, filetypes: List[str]) -> Path:
    """Find first file matching filetypes."""
    for file in path.glob(f"**/{filename}.*"):
        if file.suffix in filetypes:
            return file
    raise ConfigurationFileError(f"{path!s}/{filename}.({filetypes}) not exists!")