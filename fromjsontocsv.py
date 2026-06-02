from create_amateras_low_metadata import fromjsontocsv
from sys import argv

if __name__ == "__main__":
    argv
    fromjsontocsv(metadatafolder=argv[1], csvfile=argv[2])
