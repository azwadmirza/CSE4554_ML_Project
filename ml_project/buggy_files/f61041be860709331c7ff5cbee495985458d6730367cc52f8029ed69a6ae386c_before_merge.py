def v220_configuration_1(defaults, runtime, harmonization, dry_run):
    """
    Migrating configuration
    """
    changed = None
    for bot_id, bot in runtime.items():
        if bot["module"] == "intelmq.bots.collectors.misp.collector":
            if "misp_verify" not in bot["parameters"]:
                continue
            if bot["parameters"]["misp_verify"] != defaults["http_verify_cert"]:
                bot["parameters"]["http_verify_cert"] = bot["parameters"]["misp_verify"]
            del bot["parameters"]["misp_verify"]
            changed = True
    return changed, defaults, runtime, harmonization