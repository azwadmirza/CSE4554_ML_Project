def check_token_access(token: str) -> None:
    if token.startswith("xoxp-"):
        logging.info("This is a Slack user token, which grants all rights the user has!")
    elif token.startswith("xoxb-"):
        data = requests.get(
            "https://slack.com/api/team.info", headers={"Authorization": "Bearer {}".format(token)}
        )
        has_scopes = set(data.headers.get("x-oauth-scopes", "").split(","))
        required_scopes = set(["emoji:read", "users:read", "users:read.email", "team:read"])
        missing_scopes = required_scopes - has_scopes
        if missing_scopes:
            raise ValueError(
                "Slack token is missing the following required scopes: {}".format(
                    sorted(missing_scopes)
                )
            )
    else:
        raise Exception("Unknown token type -- must start with xoxb- or xoxp-")