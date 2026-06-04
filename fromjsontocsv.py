import os
import csv
import json
from pathlib import Path

from sys import argv


def fromjsontocsv(metadatafolder="./lowmetadata/", csvfile="./lowmetadata.csv"):
    """
    Reads every json file in folder to make a csv file from.
    """
    if not os.path.isdir(metadatafolder):
        print("Not a folder")
        return None

    metadatafolder, csvfile = Path(metadatafolder), Path(csvfile)

    starting = True
    print('Opening '+ metadatafolder.as_posix())
    list_folder = list(metadatafolder.rglob("*"))

    with open(csvfile, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for e in list_folder:
            if e.suffix == "fits":
                print(e)
                with open(e.as_posix(), 'r') as file:
                    data = json.load(file)
                    if starting:
                        writer.writerows([data.keys()])
                        starting = False
                    writer.writerows([data.values()])
    print("Finished")


if __name__ == "__main__":
    argv
    fromjsontocsv(metadatafolder=argv[1], csvfile=argv[2])
