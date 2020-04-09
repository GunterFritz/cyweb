from .structure import Structure2
import sys
import getopt

def usage():
    print("run algorithm")
    print("Options:")
    print("  s|save <filename>: saves the configuration into a file")
    print("  o|open <filename>: open the configuration from a file")
    print("  p|print:           print the configuration to stdout")
    print("  x|pers <num>:        number of person (only random configuration)")

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "s:o:px:", ['save=', 'open=', 'print', 'pers=' ])
    except getopt.GetoptError:
        usage()
        return
    s = False
    o = False
    p = False
    pers = 12
    
    struct = Structure2.factory("O")
    
    for opt, arg in opts:
        print(opt, ",", arg)
        if opt in ('-o', '--open'):
            o = True
            filename = arg
        if opt in ('-x', '--pers'):
            pers = int(arg)
        if opt in ('-s', '--save'):
            s = True
            filename = arg
        if opt in ('-p', '--print'):
            p = 'True'

    if o:
        struct.file_init(filename)
    else:
        struct.random_init(pers)
    
    struct.build()
    struct.printAgenda()
    
    if s:
        print("save to", filename)
        struct.print_out(filename)
    if p:
        struct.print_out()
#TODO: create DuplicateRule
#      cleanup

if __name__ == "__main__":
    main(sys.argv[1:])

