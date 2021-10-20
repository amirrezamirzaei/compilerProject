from scanner import Reader, ScannerResult, get_next_token

r = Reader('input.txt')
out = ScannerResult()
while get_next_token(r, out):
    pass
out.write_into_file()
