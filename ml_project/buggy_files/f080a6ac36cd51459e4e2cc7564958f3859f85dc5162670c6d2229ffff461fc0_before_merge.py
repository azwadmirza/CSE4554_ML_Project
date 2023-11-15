def get_slack_api_data(slack_api_url: str, get_param: str, **kwargs: Any) -> Any:
    if not kwargs.get("token"):
        raise AssertionError("Slack token missing in kwargs")
    data = requests.get(slack_api_url, kwargs)

    if data.status_code == requests.codes.ok:
        result = data.json()
        if not result["ok"]:
            raise Exception("Error accessing Slack API: {}".format(result["error"]))
        return result[get_param]

    raise Exception("HTTP error accessing the Slack API.")