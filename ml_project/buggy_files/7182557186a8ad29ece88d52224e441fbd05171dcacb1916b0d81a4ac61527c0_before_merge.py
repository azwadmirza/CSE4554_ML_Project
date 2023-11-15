def mksls(src, dst=None):
    """
    Convert a kickstart file to an SLS file
    """
    mode = "command"
    sls = {}
    ks_opts = {}
    with salt.utils.files.fopen(src, "r") as fh_:
        for line in fh_:
            if line.startswith("#"):
                continue

            if mode == "command":
                if line.startswith("auth ") or line.startswith("authconfig "):
                    ks_opts["auth"] = parse_auth(line)
                elif line.startswith("autopart"):
                    ks_opts["autopath"] = parse_autopart(line)
                elif line.startswith("autostep"):
                    ks_opts["autostep"] = parse_autostep(line)
                elif line.startswith("bootloader"):
                    ks_opts["bootloader"] = parse_bootloader(line)
                elif line.startswith("btrfs"):
                    ks_opts["btrfs"] = parse_btrfs(line)
                elif line.startswith("cdrom"):
                    ks_opts["cdrom"] = True
                elif line.startswith("clearpart"):
                    ks_opts["clearpart"] = parse_clearpart(line)
                elif line.startswith("cmdline"):
                    ks_opts["cmdline"] = True
                elif line.startswith("device"):
                    ks_opts["device"] = parse_device(line)
                elif line.startswith("dmraid"):
                    ks_opts["dmraid"] = parse_dmraid(line)
                elif line.startswith("driverdisk"):
                    ks_opts["driverdisk"] = parse_driverdisk(line)
                elif line.startswith("firewall"):
                    ks_opts["firewall"] = parse_firewall(line)
                elif line.startswith("firstboot"):
                    ks_opts["firstboot"] = parse_firstboot(line)
                elif line.startswith("group"):
                    ks_opts["group"] = parse_group(line)
                elif line.startswith("graphical"):
                    ks_opts["graphical"] = True
                elif line.startswith("halt"):
                    ks_opts["halt"] = True
                elif line.startswith("harddrive"):
                    ks_opts["harddrive"] = True
                elif line.startswith("ignoredisk"):
                    ks_opts["ignoredisk"] = parse_ignoredisk(line)
                elif line.startswith("install"):
                    ks_opts["install"] = True
                elif line.startswith("iscsi"):
                    ks_opts["iscsi"] = parse_iscsi(line)
                elif line.startswith("iscsiname"):
                    ks_opts["iscsiname"] = parse_iscsiname(line)
                elif line.startswith("keyboard"):
                    ks_opts["keyboard"] = parse_keyboard(line)
                elif line.startswith("lang"):
                    ks_opts["lang"] = parse_lang(line)
                elif line.startswith("logvol"):
                    if "logvol" not in ks_opts.keys():
                        ks_opts["logvol"] = []
                    ks_opts["logvol"].append(parse_logvol(line))
                elif line.startswith("logging"):
                    ks_opts["logging"] = parse_logging(line)
                elif line.startswith("mediacheck"):
                    ks_opts["mediacheck"] = True
                elif line.startswith("monitor"):
                    ks_opts["monitor"] = parse_monitor(line)
                elif line.startswith("multipath"):
                    ks_opts["multipath"] = parse_multipath(line)
                elif line.startswith("network"):
                    if "network" not in ks_opts.keys():
                        ks_opts["network"] = []
                    ks_opts["network"].append(parse_network(line))
                elif line.startswith("nfs"):
                    ks_opts["nfs"] = True
                elif line.startswith("part ") or line.startswith("partition"):
                    if "part" not in ks_opts.keys():
                        ks_opts["part"] = []
                    ks_opts["part"].append(parse_partition(line))
                elif line.startswith("poweroff"):
                    ks_opts["poweroff"] = True
                elif line.startswith("raid"):
                    if "raid" not in ks_opts.keys():
                        ks_opts["raid"] = []
                    ks_opts["raid"].append(parse_raid(line))
                elif line.startswith("reboot"):
                    ks_opts["reboot"] = parse_reboot(line)
                elif line.startswith("repo"):
                    ks_opts["repo"] = parse_repo(line)
                elif line.startswith("rescue"):
                    ks_opts["rescue"] = parse_rescue(line)
                elif line.startswith("rootpw"):
                    ks_opts["rootpw"] = parse_rootpw(line)
                elif line.startswith("selinux"):
                    ks_opts["selinux"] = parse_selinux(line)
                elif line.startswith("services"):
                    ks_opts["services"] = parse_services(line)
                elif line.startswith("shutdown"):
                    ks_opts["shutdown"] = True
                elif line.startswith("sshpw"):
                    ks_opts["sshpw"] = parse_sshpw(line)
                elif line.startswith("skipx"):
                    ks_opts["skipx"] = True
                elif line.startswith("text"):
                    ks_opts["text"] = True
                elif line.startswith("timezone"):
                    ks_opts["timezone"] = parse_timezone(line)
                elif line.startswith("updates"):
                    ks_opts["updates"] = parse_updates(line)
                elif line.startswith("upgrade"):
                    ks_opts["upgrade"] = parse_upgrade(line)
                elif line.startswith("url"):
                    ks_opts["url"] = True
                elif line.startswith("user"):
                    ks_opts["user"] = parse_user(line)
                elif line.startswith("vnc"):
                    ks_opts["vnc"] = parse_vnc(line)
                elif line.startswith("volgroup"):
                    ks_opts["volgroup"] = parse_volgroup(line)
                elif line.startswith("xconfig"):
                    ks_opts["xconfig"] = parse_xconfig(line)
                elif line.startswith("zerombr"):
                    ks_opts["zerombr"] = True
                elif line.startswith("zfcp"):
                    ks_opts["zfcp"] = parse_zfcp(line)

            if line.startswith("%include"):
                rules = shlex.split(line)
                if not ks_opts["include"]:
                    ks_opts["include"] = []
                ks_opts["include"].append(rules[1])

            if line.startswith("%ksappend"):
                rules = shlex.split(line)
                if not ks_opts["ksappend"]:
                    ks_opts["ksappend"] = []
                ks_opts["ksappend"].append(rules[1])

            if line.startswith("%packages"):
                mode = "packages"
                if "packages" not in ks_opts.keys():
                    ks_opts["packages"] = {"packages": {}}

                parser = argparse.ArgumentParser()
                opts = shlex.split(line)
                opts.pop(0)
                parser.add_argument("--default", dest="default", action="store_true")
                parser.add_argument(
                    "--excludedocs", dest="excludedocs", action="store_true"
                )
                parser.add_argument(
                    "--ignoremissing", dest="ignoremissing", action="store_true"
                )
                parser.add_argument("--instLangs", dest="instLangs", action="store")
                parser.add_argument("--multilib", dest="multilib", action="store_true")
                parser.add_argument(
                    "--nodefaults", dest="nodefaults", action="store_true"
                )
                parser.add_argument("--optional", dest="optional", action="store_true")
                parser.add_argument("--nobase", dest="nobase", action="store_true")
                args = clean_args(vars(parser.parse_args(opts)))
                ks_opts["packages"]["options"] = args

                continue

            if line.startswith("%pre"):
                mode = "pre"

                parser = argparse.ArgumentParser()
                opts = shlex.split(line)
                opts.pop(0)
                parser.add_argument("--interpreter", dest="interpreter", action="store")
                parser.add_argument(
                    "--erroronfail", dest="erroronfail", action="store_true"
                )
                parser.add_argument("--log", dest="log", action="store")
                args = clean_args(vars(parser.parse_args(opts)))
                ks_opts["pre"] = {"options": args, "script": ""}

                continue

            if line.startswith("%post"):
                mode = "post"

                parser = argparse.ArgumentParser()
                opts = shlex.split(line)
                opts.pop(0)
                parser.add_argument("--nochroot", dest="nochroot", action="store_true")
                parser.add_argument("--interpreter", dest="interpreter", action="store")
                parser.add_argument(
                    "--erroronfail", dest="erroronfail", action="store_true"
                )
                parser.add_argument("--log", dest="log", action="store")
                args = clean_args(vars(parser.parse_args(opts)))
                ks_opts["post"] = {"options": args, "script": ""}

                continue

            if line.startswith("%end"):
                mode = None

            if mode == "packages":
                if line.startswith("-"):
                    package = line.replace("-", "", 1).strip()
                    ks_opts["packages"]["packages"][package] = False
                else:
                    ks_opts["packages"]["packages"][line.strip()] = True

            if mode == "pre":
                ks_opts["pre"]["script"] += line

            if mode == "post":
                ks_opts["post"]["script"] += line

    # Set language
    sls[ks_opts["lang"]["lang"]] = {"locale": ["system"]}

    # Set keyboard
    sls[ks_opts["keyboard"]["xlayouts"]] = {"keyboard": ["system"]}

    # Set timezone
    sls[ks_opts["timezone"]["timezone"]] = {"timezone": ["system"]}
    if "utc" in ks_opts["timezone"].keys():
        sls[ks_opts["timezone"]["timezone"]]["timezone"].append("utc")

    # Set network
    if "network" in ks_opts.keys():
        for interface in ks_opts["network"]:
            device = interface.get("device", None)
            if device is not None:
                del interface["device"]
                sls[device] = {"proto": interface["bootproto"]}
                del interface["bootproto"]

                if "onboot" in interface.keys():
                    if "no" in interface["onboot"]:
                        sls[device]["enabled"] = False
                    else:
                        sls[device]["enabled"] = True
                    del interface["onboot"]

                if "noipv4" in interface.keys():
                    sls[device]["ipv4"] = {"enabled": False}
                    del interface["noipv4"]
                if "noipv6" in interface.keys():
                    sls[device]["ipv6"] = {"enabled": False}
                    del interface["noipv6"]

                for option in interface:
                    if type(interface[option]) is bool:
                        sls[device][option] = {"enabled": [interface[option]]}
                    else:
                        sls[device][option] = interface[option]
            if "hostname" in interface:
                sls["system"] = {
                    "network.system": {
                        "enabled": True,
                        "hostname": interface["hostname"],
                        "apply_hostname": True,
                    }
                }

    # Set selinux
    if "selinux" in ks_opts.keys():
        for mode in ks_opts["selinux"]:
            sls[mode] = {"selinux": ["mode"]}

    # Get package data together
    if "nobase" not in ks_opts["packages"]["options"]:
        sls["base"] = {"pkg_group": ["installed"]}

    packages = ks_opts["packages"]["packages"]
    for package in packages:
        if not packages[package]:
            continue
        if package and packages[package] is True:
            if package.startswith("@"):
                pkg_group = package.replace("@", "", 1)
                sls[pkg_group] = {"pkg_group": ["installed"]}
            else:
                sls[package] = {"pkg": ["installed"]}
        elif packages[package] is False:
            sls[package] = {"pkg": ["absent"]}

    if dst:
        with salt.utils.files.fopen(dst, "w") as fp_:
            salt.utils.yaml.safe_dump(sls, fp_, default_flow_style=False)
    else:
        return salt.utils.yaml.safe_dump(sls, default_flow_style=False)