import os
import csv
import json
from pathlib import Path

from sys import argv


def fromjsontocsv(metadatafolder="./lowmetadata/", csvpath="./lowmetadata.csv"):
    """
    Reads every json file in folder to make a csv file from.
    """
    if not os.path.isdir(metadatafolder):
        print("Not a folder")
        return None

    metadatafolder, csvfile = Path(metadatafolder), Path(csvpath)

    starting = True
    print('Opening ' + metadatafolder.as_posix())
    print('Opening ' + metadatafolder.as_posix())
    list_folder = list(metadatafolder.rglob("*"))
    print(str(len(list_folder)) + "elements")
    with open(csvpath.as_posix(), mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for e in list_folder:
            if e.suffix == ".json":
                with open(e.as_posix(), 'r') as file:
                    data = json.load(file)
                    print(data)
                    if starting:
                        writer.writerows([data.keys()])
                        starting = False
                    writer.writerows([data.values()])
    print("Finished")


if __name__ == "__main__":
    argv
    fromjsontocsv(metadatafolder=argv[1], csvpath=argv[2])
