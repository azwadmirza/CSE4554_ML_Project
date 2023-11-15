def _proxies_to_dispatchers(
    proxies: typing.Optional[ProxiesTypes]
) -> typing.Dict[str, AsyncDispatcher]:
    if proxies is None:
        return {}
    elif isinstance(proxies, (str, URL)):
        return {"all": _proxy_from_url(proxies)}
    elif isinstance(proxies, AsyncDispatcher):
        return {"all": proxies}
    else:
        new_proxies = {}
        for key, dispatcher_or_url in proxies.items():
            if isinstance(dispatcher_or_url, (str, URL)):
                new_proxies[str(key)] = _proxy_from_url(dispatcher_or_url)
            else:
                new_proxies[str(key)] = dispatcher_or_url
        return new_proxies