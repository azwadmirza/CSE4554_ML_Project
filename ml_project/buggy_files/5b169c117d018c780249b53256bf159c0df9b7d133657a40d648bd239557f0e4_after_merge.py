def main(*args):
    parser = argparse.ArgumentParser(
            description="""
                Merge one or more github pull requests by their number. If any
                one pull request can't be merged as is, its merge is ignored
                and the process continues with the next ones (if any).
                """
            )

    grp = parser.add_mutually_exclusive_group()
    grp.add_argument(
            '-l',
            '--list',
            action='store_const',
            const=True,
            help='list PR, their number and their mergeability')
    grp.add_argument('-a',
            '--merge-all',
            action='store_const',
            const=True ,
            help='try to merge as many PR as possible, one by one')
    parser.add_argument('integers',
            type=int,
            help="The pull request numbers",
            nargs='*',
            metavar='pr-number')
    args = parser.parse_args()

    if(args.list):
        pr_list = gh_api.get_pulls_list(gh_project)
        for pr in pr_list :
            mergeable = gh_api.get_pull_request(gh_project, pr['number'])['mergeable']

            ismgb = u"√" if mergeable else " "
            print(u"* #{number} [{ismgb}]:  {title}".format(
                number=pr['number'],
                title=pr['title'],
                ismgb=ismgb))

    if(args.merge_all):
        pr_list = gh_api.get_pulls_list(gh_project)
        for pr in pr_list :
            merge_pr(pr['number'])


    elif args.merge:
        for num in args.merge :
            merge_pr(num)

    if not_merged :
        print('*************************************************************************************')
        print('the following branch have not been merged automatically, considere doing it by hand :')
        for num, cmd in not_merged.items() :
            print( "PR {num}: {cmd}".format(num=num, cmd=cmd))
        print('*************************************************************************************')