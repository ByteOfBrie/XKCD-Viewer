import sys

sys.path.append('..')

from XKCDParser import XKCDParser

def main():
    parser = XKCDParser()
    parser.set_id(710)
    print(str(parser.img).replace("', '", '\n'))

if __name__ == '__main__':
    main()
