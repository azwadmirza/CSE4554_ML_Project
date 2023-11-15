def install_centos_new(args: CommandLineArguments, root: str, epel_release: int) -> List[str]:
    # Repos for CentOS 8 and later

    gpgpath="/etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial"
    gpgurl='https://www.centos.org/keys/RPM-GPG-KEY-CentOS-Official'
    epel_gpgpath = f"/etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-{epel_release}"
    epel_gpgurl = f'https://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-{epel_release}'

    if args.mirror:
        appstream_url = f"baseurl={args.mirror}/centos/{args.release}/AppStream/x86_64/os"
        baseos_url = f"baseurl={args.mirror}/centos/{args.release}/BaseOS/x86_64/os"
        extras_url = f"baseurl={args.mirror}/centos/{args.release}/extras/x86_64/os"
        centosplus_url = f"baseurl={args.mirror}/centos/{args.release}/centosplus/x86_64/os"
        epel_url = f"baseurl={args.mirror}/epel/{epel_release}/Everything/x86_64/os"
    else:
        appstream_url = f"mirrorlist=http://mirrorlist.centos.org/?release={args.release}&arch=x86_64&repo=AppStream"
        baseos_url = f"mirrorlist=http://mirrorlist.centos.org/?release={args.release}&arch=x86_64&repo=BaseOS"
        extras_url = f"mirrorlist=http://mirrorlist.centos.org/?release={args.release}&arch=x86_64&repo=extras"
        centosplus_url = f"mirrorlist=http://mirrorlist.centos.org/?release={args.release}&arch=x86_64&repo=centosplus"
        epel_url = f"mirrorlist=https://mirrors.fedoraproject.org/mirrorlist?repo=epel-{epel_release}&arch=x86_64"

    setup_dnf(args, root, repos=[
        Repo("AppStream", f"CentOS-{args.release} - AppStream", appstream_url, gpgpath, gpgurl),
        Repo("BaseOS", f"CentOS-{args.release} - Base", baseos_url, gpgpath, gpgurl),
        Repo("extras", f"CentOS-{args.release} - Extras", extras_url, gpgpath, gpgurl),
        Repo("centosplus", f"CentOS-{args.release} - Plus", centosplus_url, gpgpath, gpgurl),
        Repo("epel", f"name=Extra Packages for Enterprise Linux {epel_release} - $basearch", epel_url, epel_gpgpath, epel_gpgurl),
    ])

    return ["AppStream", "BaseOS", "extras", "centosplus"]