def export_items():
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "scope": [
            {
                "target": item.target,
                "blacklist": item.blacklist,
                "tags": item.get_tag_names(),
            }
            for item in ScopeItem.getScope()
        ],
        "blacklist": [
            {
                "target": item.target,
                "blacklist": item.blacklist,
                "tags": item.get_tag_names(),
            }
            for item in ScopeItem.getBlacklist()
        ],
    }
    print(json.dumps(result, indent=2))