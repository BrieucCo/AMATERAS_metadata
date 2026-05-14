from astropy.io import fits
from astropy.time import Time
import os
import datetime
import sys
import json


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


def create_low_metadata(folder_FITS, folder_metadata):
    """
    Parameters:
    folder_FITS: str
        - Can be either a single fits file or a folder containing fits file
        -
    folder_metadata: str
        - Folder where the metadata files will be saved (must already exist)
    Returns:
    None

    This code reads the header in each fits file in folder_FITS and
    create a metadata json file for each of them
    """

    if os.path.isdir(folder_FITS):
        # if folder_FITS is a folder: create a list of files in folder
        if folder_FITS[-1] != "/":
            print("Data Folder is missing / at the end: Adding / at the end.")
            folder_FITS += "/"
        list_file = os.listdir(folder_FITS)
    elif os.path.isfile(
        folder_FITS
    ):  # if folder_FITS is a file: create a one element list of the given file
        print("Single file detected")
        list_file = [None]
        folder_FITS, list_file[0] = os.path.split(folder_FITS)
        folder_FITS += "/"
    else:
        print("ERROR: Data folder does not exist: " + folder_FITS)
        exit()

    if len(list_file) == 0:
        print("ERROR: Data folder is empty" + folder_FITS)
        return None

    if os.path.isdir(folder_metadata) is False:
        print("ERROR: Metadata folder does not exist" + folder_metadata)
        exit()

    metadata_template = [
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
        "c1min",
        "c1max",
        "c2min",
        "c2max",
        "c3min",
        "c3max",
        "s_region",
        "c1_resol_min",
        "c1_resol_max",
        "c2_resol_min",
        "c2_resol_max",
        "c3_resol_min",
        "c3_resol_max",
        "spatial_frame_type",
        "incidence_min",
        "incidence_max",
        "emergence_min",
        "emergence_max",
        "phase_min",
        "phase_max",
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
        "access_md5",
        "thumbnail_url",
        "species",
        "publisher",
        "bib_reference",
        "target_region",
        "feature_name",
        "datalink_url",
        "receiver_name",
        "relative_path",
        "date_meridian",
        "spectral_bandwith_min",
        "spectral_bandwith_max",
    ]  # create list of keys from template file

    meta = dict.fromkeys(
        metadata_template
    )  # create an empty dictionnary with the needed kys

    for filename in list_file:  # iterate all files in folder_FITS

        if filename[-4:] == "fits":
            header = fits.getheader(folder_FITS + filename, 0)  # read FITS header
        else:
            print(folder_FITS + filename + " is not a FITS. Skipping this file")
            continue

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
            print("KeyError in " + folder_FITS + filename)
            continue

        if header["BITPIX"] != 8:
            print(folder_FITS + filename + " is not a 8 bit file")
            continue

        # Instrument metadata from FITS header
        try:
            meta["receiver_name"] = header["INSTRUME"]
            meta["instrument_host_name"] = header["ORIGIN"]
            meta["instrument_name"] = header["TELESCOP"]  # INSTRUME?
        except:
            print(f"Instrument error: check INSTRUME, ORIGIN and TELESCOP field. \
                    Skipping {filename}")
            continue

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
        except:
            print(f"DATE error: check DATE-OBS, TIME-OBS, DATE-END and \
                    TIME-END fields. Skipping {filename}")
            continue

        # Time metadata from file metadata
        try:
            meta["creation_date"] = datetime.datetime.fromtimestamp(
                os.path.getctime(folder_FITS + filename)
            ).isoformat()[
                :-3
            ]  # from file date but should be when the granule was introduced in the service
            meta["modification_date"] = datetime.datetime.fromtimestamp(
                os.path.getmtime(folder_FITS + filename)
            ).isoformat()[
                :-3
            ]  # from file date but should be when the granule was introduced in the
            meta["access_estsize"] = os.path.getsize(folder_FITS + filename) / 1e3
        except:
            print("Problem with file metadata. Skipping " + filename)
            continue

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

        except:
            print("Problem with DATE field in header. Skipping " + filename)
            continue

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
            "phys.flux.density;em.radio;phys.polarization"  # hash separated list ?
        )
        meta["processing_level"] = 1  # unit is db above quiet Sun lvl

        ##Time resolution
        meta["time_sampling_step_min"] = 1  # time between 2 successive measurements
        meta["time_sampling_step_max"] = 1  # time between 2 successive measurements

        meta["time_exp_min"] = 1  # integration time
        meta["time_exp_max"] = 1  # integration time

        meta["time_scale"] = "UTC"

        ##Spetral resolution
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

        ## Access
        meta["access_format"] = "application/fits"

        meta["bib_reference"] = "10.1007/s11207-011-9919-y"

        # Create json file in folder_metadata
        json_name = folder_metadata + filename[:-5] + "_metadata.json"
        with open(json_name, "w") as json_file:
            json.dump(meta, json_file, indent=4)
        print("Metadata successfully saved to " + json_name)


# Use in terminal python create_amateras_low_metadata.py FOLDER_data folder_metadata
# can also give a single data file instead of folder_data
if __name__ == "__main__":
    try:  # Verify folder_FITS is given
        folder_FITS = str(sys.argv[1]).replace("\\", "/")

    except:
        folder_FITS = "./low/"
        print("FITS Folder not given. Using default: " + folder_FITS)

    try:  # Verify folder_metadata is given
        folder_metadata = str(sys.argv[2]).replace("\\", "/")
    except:
        folder_metadata = "./lowmetadata/"
        print("Metadata Folder not given. Using default: " + folder_metadata)

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

        if all(os.path.isdir(os.path.join(folder_FITS, e)) for e in L_folder):
            # if there are only folders inside folder_FITS
            # create same subfolders for folder_metadata
            print("Folders detected in " + folder_FITS)
            for subfolder_FITS in L_folder:
                if not os.path.isdir(folder_metadata + subfolder_FITS):
                    # if subfolder_FITS not in folder_metadata then create it.
                    os.makedirs(folder_metadata + subfolder_FITS)

                create_low_metadata(
                    folder_FITS + subfolder_FITS + "/",
                    folder_metadata + subfolder_FITS + "/",
                )
        else:
            create_low_metadata(folder_FITS, folder_metadata)
    else:
        create_low_metadata(folder_FITS, folder_metadata)
    delete_empty_folders(folder_metadata)
