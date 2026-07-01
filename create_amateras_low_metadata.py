from astropy.io import fits
from astropy.time import Time
import os
import datetime
import sys
import json
import csv
from pathlib import Path
from alive_progress import alive_it
# import logging
# import warnings

METADATA_KEYS = [
    "granule_uid",
    "granule_gid",
    "obs_id",
    "dataproduct_type",
    "target_name",
    "target_class",
    "time_min",
    "time_max",
    "time_sampling_step_min",
    "time_sampling_step_max",
    "time_exp_min",
    "time_exp_max",
    "spectral_range_min",
    "spectral_range_max",
    "spectral_sampling_step_min",
    "spectral_sampling_step_max",
    "spectral_resolution_min",
    "spectral_resolution_max",
    "spatial_frame_type",
    "instrument_host_name",
    "instrument_name",
    "measurement_type",
    "processing_level",
    "creation_date",
    "modification_date",
    "release_date",
    "service_title",
    "access_url",
    "file_name",
    "access_format",
    "access_estsize",
    "time_scale",
    # "access_md5",
    "thumbnail_url",
    "publisher",
    "bib_reference",
    "target_region",
    "feature_name",
    # "datalink_url",
    "receiver_name",
    "spectral_bandwith_min",
    "spectral_bandwith_max",
]  # create a global list of needed kys


def delete_empty_folders(root):

    deleted = set()

    for current_dir, subdirs, files in os.walk(root, topdown=False):

        still_has_subdirs = False
        for subdir in subdirs:
            if os.path.join(current_dir, subdir) not in deleted:
                still_has_subdirs = True
                break

        if not any(files) and not still_has_subdirs:
            os.rmdir(current_dir)
            deleted.add(current_dir)

    return deleted


def create_low_metadata(file_FITS):
    """
    Parameters:
    file_FITS: str | pathlib.Path
        - Can be either a single fits file
        -
    Returns:
    dict containing metadata
    None if error

    This code reads the header of file_FITS and
    create a metadata dict for it
    """

    file_FITS = Path(file_FITS)
    filepath = file_FITS.as_posix()
    if file_FITS.is_file() is False:
        print("ERROR: File does not exist: " + file_FITS.name)
        return None

    filename = file_FITS.name
    if file_FITS.suffix == ".fits":
        header = fits.getheader(file_FITS, 0)  # read FITS header
        # with warnings.catch_warnings(record=True) as w:
        #     warnings.simplefilter("always")  # force all warnings in bloc to be seen even if previously seen
        #     header = fits.getheader(file_FITS, 0)  # read FITS header
        #     for warning in w:
        #         logger.warning(
        #             "%s: %s", filename, str(warning.message)
        #         )

    else:
        print(filepath + " is not a FITS. Skipping this file")
        return None
    if any(
        [
            e not in header.keys()
            for e in [
                "BITPIX",
                "INSTRUME",
                "ORIGIN",
                "TELESCOP",
                "DATE-OBS",
                "TIME-OBS",
                "DATE-END",
                "TIME-END",
                "DATE",
            ]
        ]
    ):
        print("KeyError in " + filepath)
        return None

    if header["BITPIX"] != 8:
        print(filepath + " is not a 8 bit file")
        return None

    meta = dict.fromkeys(
        METADATA_KEYS
    )  # create an empty dictionnary with the needed kys

    meta["spatial_frame_type"] = "none"

    # Instrument metadata from FITS header
    try:
        meta["receiver_name"] = header["INSTRUME"]
        meta["instrument_host_name"] = "Itate Observatory"  # header["ORIGIN"]
        meta["instrument_name"] = header["TELESCOP"]  # INSTRUME?
        meta["service_title"] = "iprt"
        meta["publisher"] = "Tohoku University"
    except KeyError:
        print(f"Instrument error: check INSTRUME, ORIGIN and TELESCOP field. \
                Skipping {filepath}")
        return None

    # Time metadata from FITS header
    try:
        t_beg = Time(header["DATE-OBS"] + "T" + header["TIME-OBS"])
        t_end = Time(header["DATE-END"] + "T" + header["TIME-END"])

        meta["time_min"] = t_beg.jd1 + t_beg.jd2
        meta["time_max"] = t_end.jd1 + t_end.jd2
        meta["access_url"] = (
            "http://radio.gp.tohoku.ac.jp/db/IPRT-SUN/DATA2/"
            + header["DATE-OBS"][:4]
            + "/"
            + filename
        )
    except KeyError:
        print(f"DATE error: check DATE-OBS, TIME-OBS, DATE-END and \
                TIME-END fields. Skipping {filepath}")
        return None
    except TypeError:
        print(f"DATE error: Type error with {filename}")

    # Time metadata from file metadata
    try:
        meta["creation_date"] = datetime.datetime.fromtimestamp(
            os.path.getctime(filepath)
        ).isoformat()[
            :-3
        ]  # from file date but should be when the granule was introduced in the service
        meta["modification_date"] = datetime.datetime.fromtimestamp(
            os.path.getmtime(filepath)
        ).isoformat()[
            :-3
        ]  # from file date but should be when the granule was introduced in the
        meta["release_date"] = meta["modification_date"]
        meta["access_estsize"] = os.path.getsize(filepath) / 1e3
    except TypeError:
        raise TypeError("filepath is probably not a str " + filename)
        return None
    except:
        print("Problem with file metadata. Skipping " + filename)
        return None

    # metadata from file name
    try:
        Time(header["DATE"])
        meta["granule_uid"] = (
            "iprt_amateras_low_" + header["DATE"].replace("-", "") + "_v1.0"
        )  #
        meta["thumbnail_url"] = (
            "http://radio.gp.tohoku.ac.jp/sun_ql/plot/IPRT_SUN_"
            + header["DATE"].replace("-", "")
            + ".gif"
        )
    except KeyError:
        print("Problem with DATE field in header. Skipping " + filename)
        return None
    except AttributeError:
        print("Problem with DATE field in header. Skipping " + filename)
        return None

    meta["file_name"] = filename  # ??
    meta["obs_id"] = meta["granule_uid"]  # same as above

    # Constant metadata
    meta["granule_gid"] = "IPRT AMATERAS Low Resolution Dataset"  # ??
    meta["dataproduct_type"] = "ds"
    meta["target_name"] = "Sun"
    meta["target_class"] = "star"
    meta["target_region"] = "SolarWind#Heliosphere"
    meta["feature_name"] = "Solar radio bursts"
    meta["measurement_type"] = (
        "phot.flux.density;em.radio;phys.polarization"  # hash separated list ?
    )
    meta["processing_level"] = 1  # unit is db above quiet Sun lvl

    #Time resolution
    meta["time_sampling_step_min"] = 1  # time between 2 successive measurements
    meta["time_sampling_step_max"] = 1  # time between 2 successive measurements

    meta["time_exp_min"] = 1  # integration time
    meta["time_exp_max"] = 1  # integration time

    meta["time_scale"] = "UTC"

    # Spetral resolution
    meta["spectral_range_min"] = int(100e6)
    meta["spectral_range_max"] = int(500e6)
    meta["spectral_resolution_min"] = 500.0  # f/df
    meta["spectral_resolution_max"] = 100.0  # f/df

    meta["spectral_sampling_step_min"] = (
        0.976562e6  # frequency between 2 successive measurements
    )
    meta["spectral_sampling_step_max"] = (
        0.976562e6  # frequency between 2 successive measurements
    )
    meta["spectral_bandwith_min"] = 0.976562e6  # bandwidth of 1 MHz
    meta["spectral_bandwith_max"] = 0.976562e6  # bandwidth of 1 MHz

    # Access
    meta["access_format"] = "application/fits"

    meta["bib_reference"] = "10.1007/s11207-011-9919-y"
    return meta


def verify_input_paths(paths, defaults='low'):

    if defaults == 'low':
        default_folder_fits = "./examples/low/"
        default_folder_metadata = "./lowmetadata/"
    elif defaults == 'high16':
        default_folder_fits = "./examples/high16/"
        default_folder_metadata = "./high16metadata/"
    elif defaults == 'high08':
        default_folder_fits = "./examples/high08/"
        default_folder_metadata = "./high08metadata/"

    """ Verify the inputs if any
    Returns pathlib of the folders"""
    
    try:  # Verify folder_FITS is given
        folder_FITS = str(paths[1]).replace("\\", "/")
    except IndexError:
        folder_FITS = default_folder_fits  # "./examples/low/"
        print("FITS Folder not given. Using default: " + folder_FITS)

    try:  # Verify folder_metadata is given
        folder_metadata = str(paths[2]).replace("\\", "/")
    except IndexError:
        folder_metadata = default_folder_metadata  # "./lowmetadata/"
        print("Metadata Folder not given. Using default: " + folder_metadata)

    if len(paths) >= 5:
        create_csv, create_json = bool(int(paths[3])), bool(int(paths[4]))
    else:
        create_csv, create_json = True, True

    if folder_metadata[-1] != "/":
        folder_metadata += "/"
        print("Metadata Folder is missing / at the end: Adding / at the end.")

    if folder_FITS[-1] != "/":
        folder_FITS += "/"
        print("Metadata Folder is missing / at the end: Adding / at the end.")
    if os.path.isdir(folder_metadata) is False:
        print("Creating " + folder_metadata)
        os.makedirs(folder_metadata)

    if os.path.isdir(folder_FITS):
        L_folder = os.listdir(folder_FITS)
        if len(L_folder) == 0:
            print(folder_FITS + " is empty")
            exit()
    # Create metadata folder if doesnt exist
    Path(folder_metadata).mkdir(parents=True, exist_ok=True)

    return Path(folder_FITS), Path(folder_metadata), create_csv, create_json


def browse_save(
    folder_FITS_path,
    folder_metadata_path,
    csv_filename,
    metadata_creator,
    create_csv=True,
    create_json=True
):
    with open(csv_filename, mode='w', newline='') as csvfile:
        # Initialize csv file
        if create_csv:
            writer = csv.writer(csvfile)
            writer.writerows([METADATA_KEYS])

        # Browse folder_FITS
        if folder_FITS_path.is_file and not folder_FITS_path.is_dir:
            print(f'only one file detected: {str(folder_FITS_path)}')
            iterator = [folder_FITS_path]
        else:
            iterator = list(folder_FITS_path.rglob("*"))
        print('Starting: '+len(iterator))
        for e in alive_it(iterator):
            # if element is folder create equivalent folder in metadata folder
            if any(err in e.as_posix() for err in ["old", "misc", "Original", "Revised", "misc"]):
                continue
            if e.is_dir() and create_json:
                target = folder_metadata_path / e.relative_to(folder_FITS_path)
                target.mkdir(parents=True, exist_ok=True)

            # If element is fits create a python dict containing metadata
            elif e.name.endswith('.fits'):  # if fits
                dict_metadata = metadata_creator(e)
                if dict_metadata is not None:
                    # Create json file in folder_metadata
                    if create_json:
                        json_name = folder_metadata_path / (
                            e.parent.relative_to(folder_FITS_path) / (
                                e.name[:-5] + "_metadata.json"
                            )
                        )
                        with open(json_name, "w") as json_file:
                            json.dump(dict_metadata, json_file, indent=4)
                        # print("Metadata successfully saved to " + json_name.name)
                    # Add row in csv file
                    if create_csv:
                        writer.writerows([dict_metadata.values()])

    if not create_csv:
        os.remove(csv_filename)
    if create_json:
        delete_empty_folders(folder_metadata_path.as_posix())


# Config log file
# logging.basicConfig(
#     filename="fits_warnings.log",
#     level=logging.WARNING,
#     format="%(asctime)s %(levelname)s %(message)s"
# )

# logger = logging.getLogger(__name__)


# Use in terminal python create_amateras_low_metadata.py FOLDER_data folder_metadata
# can also give a single data file instead of folder_data
if __name__ == "__main__":
    (folder_FITS_path, folder_metadata_path,
        create_csv, create_json) = verify_input_paths(sys.argv)

    if create_csv is False and create_json is False:
        print('Select one of the output return')
        exit()

    if create_csv:
        csv_filename = folder_metadata_path / "IPRT_low_metadata_table.csv"
    else:
        csv_filename = folder_metadata_path / "empty"

    browse_save(folder_FITS_path, folder_metadata_path,
                csv_filename, create_low_metadata, create_csv, create_json)
    print("Finished")
