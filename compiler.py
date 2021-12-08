# Amirreza Mirzaei 98106112         Arman Soleimani 98105835

from anytree import RenderTree
from parsers.parser_transition_diagram import parse_transition_diagram


def write_to_file(tree, errors):
    tree_str = ''
    for pre, fill, node in RenderTree(tree):
        tree_str += "%s%s" % (pre, node.name) + '\n'

    f = open("parse_tree.txt", "w", encoding='utf-8')
    f.write(tree_str.strip())
    f.close()

    f = open("syntax_errors.txt", "w")
    if errors:
        for item in errors:
            f.write("%s\n" % item)
    else:
        f.write('There is no syntax error.')
    f.close()


tree, errors = parse_transition_diagram()
write_to_file(tree, errors)
