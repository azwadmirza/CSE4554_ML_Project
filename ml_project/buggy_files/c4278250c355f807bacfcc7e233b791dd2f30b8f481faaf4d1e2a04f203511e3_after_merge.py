def translate(configuration: Dict[str, Any],
              dictionary: Dict[str, str]) -> Dict[str, Any]:
    return {
        dictionary[field]: configuration[field]
        for field in dictionary if field in configuration
    }