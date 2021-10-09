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
        self.f.seek(index)
