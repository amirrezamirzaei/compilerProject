from parser import parse
from anytree import RenderTree


def write_to_file(tree, errors):
    tree_str = ''
    for pre, fill, node in RenderTree(tree):
        tree_str += "%s%s" % (pre, node.name) + '\n'

    f = open("parse_tree.txt", "w")
    f.write(tree_str.strip())
    f.close()

    f = open("syntax_errors.txt", "w")
    if errors:
        for item in errors:
            f.write("%s\n" % item)
    else:
        f.write('There is no syntax error.')
    f.close()


tree, errors = parse()
write_to_file(tree, errors)
