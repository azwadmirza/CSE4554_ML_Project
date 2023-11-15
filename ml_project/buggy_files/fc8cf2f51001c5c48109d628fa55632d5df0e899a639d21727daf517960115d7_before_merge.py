def printable_folders(folders: Dict[str, Optional[Link]],
                      json: bool=False,
                      csv: Optional[str]=None) -> str:
    if json: 
        return to_json(folders.values(), indent=4, sort_keys=True)

    elif csv:
        return links_to_csv(folders.values(), cols=csv.split(','), header=True)
    
    return '\n'.join(f'{folder} {link}' for folder, link in folders.items())