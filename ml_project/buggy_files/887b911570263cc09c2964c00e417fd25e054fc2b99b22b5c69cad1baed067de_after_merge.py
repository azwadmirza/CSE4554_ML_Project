def _on_message(body, message):
    try:
        branch = body["payload"]["data"]["repo_url"].split("/")[-1]
        rev = body["payload"]["data"]["heads"][0]

        if branch in ["autoland", "try"]:
            user = body["payload"]["data"]["pushlog_pushes"][0]["user"]
            if user in ("reviewbot", "wptsync@mozilla.com"):
                return

            url = "{}/push/{}/{}/schedules".format(BUGBUG_HTTP_SERVER, branch, rev)
            response = requests.get(url, headers={"X-Api-Key": "pulse_listener"})
            if response.status_code == 202:
                logger.info("Successfully requested {}/{}".format(branch, rev))
            else:
                logger.warning(
                    "We got status: {} for: {}".format(response.status_code, url)
                )
    except Exception:
        traceback.print_exc()
    finally:
        message.ack()