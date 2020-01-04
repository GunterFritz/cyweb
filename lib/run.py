from structure import Oktaeder2
import sys
import getopt

def usage():
    print("run algorithm")

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "s:o:p", ['save=', 'open=', 'print' ])
    except getopt.GetoptError:
        usage()
        return
    s = False
    o = False
    p = False
    
    struct = Oktaeder2()
    
    for opt, arg in opts:
        print(opt, ",", arg)
        if opt in ('-o', '--open'):
            o = True
            filename = arg
        if opt in ('-s', '--save'):
            s = True
            filename = arg
        if opt in ('-p', '--print'):
            p = 'True'

    if o:
        struct.file_init(filename)
    else:
        struct.random_init(12)
    
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

