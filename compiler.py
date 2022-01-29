# Amirreza Mirzaei 98106112         Arman Soleimani 98105835
from anytree import RenderTree

from parsers.parser_transition_diagram import parse_transition_diagram


def write_to_file(code, errors, tree):
    tree_str = ''
    for pre, fill, node in RenderTree(tree):
        tree_str += "%s%s" % (pre, node.name) + '\n'
    f = open("parse_Tree.txt", "w", encoding='utf-8')
    f.write(tree_str.strip())
    f.close()

    if semantic_errors:
        string_to_write = ''
        for error in semantic_errors:
            string_to_write += error + '\n'

        f = open("semantic_errors.txt", "w", encoding='utf-8')
        f.write(string_to_write.strip())
        f.close()
    else:
        string_to_write = ''
        for line in code:
            string_to_write += line + '\n'

        f = open("output.txt", "w", encoding='utf-8')
        f.write(string_to_write.strip())
        f.close()

        f = open("expected.txt", "w")
        f.write('will be added.')
        f.close()

        f = open("semantic_errors.txt", "w")
        f.write('The input program is semantically correct.')
        f.close()


tree, parse_errors, three_address_code, semantic_errors = parse_transition_diagram()
write_to_file(three_address_code, semantic_errors, tree)