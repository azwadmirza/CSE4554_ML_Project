def convert_files_to_dicts(dir_path: str, clean_func: Optional[Callable] = None, split_paragraphs: bool = False) -> List[dict]:
    """
    Convert all files(.txt, .pdf) in the sub-directories of the given path to Python dicts that can be written to a
    Document Store.

    :param dir_path: path for the documents to be written to the DocumentStore
    :param clean_func: a custom cleaning function that gets applied to each doc (input: str, output:str)
    :param split_paragraphs: split text in paragraphs.

    :return: None
    """

    file_paths = [p for p in Path(dir_path).glob("**/*")]
    if ".pdf" in [p.suffix.lower() for p in file_paths]:
        pdf_converter = PDFToTextConverter()  # type: Optional[PDFToTextConverter]
    else:
        pdf_converter = None

    documents = []
    for path in file_paths:
        if path.suffix.lower() == ".txt":
            with open(path) as doc:
                text = doc.read()
        elif path.suffix.lower() == ".pdf" and pdf_converter:
            document = pdf_converter.convert(path)
            text = document["text"]
        else:
            raise Exception(f"Indexing of {path.suffix} files is not currently supported.")

        if clean_func:
            text = clean_func(text)

        if split_paragraphs:
            for para in text.split("\n\n"):
                if not para.strip():  # skip empty paragraphs
                    continue
                documents.append({"text": para, "meta": {"name": path.name}})
        else:
            documents.append({"text": text, "meta": {"name": path.name}})

    return documents