def print_msg(template, msg):
    print(template.format(msg.rstrip().encode('utf-8')))