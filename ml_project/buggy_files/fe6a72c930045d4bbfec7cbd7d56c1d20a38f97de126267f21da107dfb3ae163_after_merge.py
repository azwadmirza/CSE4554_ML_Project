    def sort_locals(my_list):
        my_list.sort(key=lambda node: node.fromlineno or 0)