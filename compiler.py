import sys


class Reader:

    def __init__(self, file_name):
        self.f = open(file_name, "r")
        self.character_index = 0

    def get_next_character(self):
        c = self.f.read(1)
        self.character_index = self.f.tell()
        return c

    def revert(self, index):
        self.character_index = self.character_index-index
        self.f.seek(self.character_index)


assert len(sys.argv) == 2
file_name = sys.argv[1]
r = Reader(file_name)
