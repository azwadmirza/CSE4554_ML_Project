def find_one_filetype(
    path: Path, filename: str, filetypes: List[str]
) -> Optional[Path]:
    """Find first file matching filetypes."""
    for file in path.glob(f"**/{filename}.*"):
        if file.suffix in filetypes:
            return file
    return None