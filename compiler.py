from parser import parse
from anytree import Node, RenderTree

tree, error = parse()

tree_str = ''
for pre, fill, node in RenderTree(tree):
    tree_str += "%s%s" % (pre, node.name) + '\n'

text_file = open("parse_tree.txt", "w")
text_file.write(tree_str.strip())
text_file.close()

text_file = open("syntax_errors.txt", "w")
text_file.write(error)
text_file.close()