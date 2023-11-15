def normalize_launch_params(params: Dict) -> None:
    if "env" in params:
        params["env"] = {name: str(value) for [name, value] in params["env"].items()}
    if "ignoreDefaultArgs" in params:
        if isinstance(params["ignoreDefaultArgs"], bool):
            params["ignoreAllDefaultArgs"] = True
            del params["ignoreDefaultArgs"]
        params["env"] = {name: str(value) for [name, value] in params["env"].items()}
    if "executablePath" in params:
        params["executablePath"] = str(Path(params["executablePath"]))
    if "downloadsPath" in params:
        params["downloadsPath"] = str(Path(params["downloadsPath"]))