from astropy.io import fits
from astropy.time import Time
import os
import datetime
import sys
from create_amateras_low_metadata import verify_input_paths, browse_save
from pathlib import Path

METADATA_KEYS_HIGH = [
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
    # "c1min",
    # "c1max",
    # "c2min",
    # "c2max",
    # "c3min",
    # "c3max",
    # "s_region",
    # "c1_resol_min",
    # "c1_resol_max",
    # "c2_resol_min",
    # "c2_resol_max",
    # "c3_resol_min",
    # "c3_resol_max",
    "spatial_frame_type",
    # "incidence_min",
    # "incidence_max",
    # "emergence_min",
    # "emergence_max",
    # "phase_min",
    # "phase_max",
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
    # "relative_path",
    # "date_meridian",
    "spectral_bandwith_min",
    "spectral_bandwith_max",
]


def create_high16_metadata(file_FITS):
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

    if header["BITPIX"] != 16:
        print(filepath + " is not a 16 bit file")
        return None

    meta = dict.fromkeys(
        METADATA_KEYS_HIGH
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
            "http://octave.gp.tohoku.ac.jp/db/IPRT-SUN/l1/high16/{}/{}/{}".format(
                header["DATE"][:4],
                header["DATE"].replace("-", ""),
                filename,
            )
        )
    except KeyError:
        print(f"DATE error: check DATE-OBS, TIME-OBS, DATE-END and \
                TIME-END fields. Skipping {filepath}")
        return None
    except TypeError:
        print(f"DATE error: Type error with {filename}")
        return None

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
        meta["granule_uid"] = (
            "iprt_amateras_high_16bit{}_v1.0".format(filename[-22:-9])
        )
        meta["thumbnail_url"] = (
            "http://octave.gp.tohoku.ac.jp/db/IPRT-SUN/l1/png/high16/{}/{}/{}.png".format(
                header["DATE"][:4],
                header["DATE"].replace("-", ""),
                filename[:-5],
            )
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
    meta["granule_gid"] = "IPRT AMATERAS High Resolution 16 bit Dataset"  # ??
    meta["dataproduct_type"] = "ds"
    meta["target_name"] = "Sun"
    meta["target_class"] = "star"
    meta["target_region"] = "SolarWind#Heliosphere"
    meta["feature_name"] = "Solar radio bursts"
    meta["measurement_type"] = (
        "phot.flux.density;em.radio;phys.polarization"  # hash separated list ?
    )
    meta["processing_level"] = 1  # unit is db above quiet Sun lvl

    # Time resolution
    meta["time_sampling_step_min"] = 1  # time between 2 successive measurements
    meta["time_sampling_step_max"] = 1  # time between 2 successive measurements

    meta["time_exp_min"] = 0.01  # integration time
    meta["time_exp_max"] = 0.01  # integration time

    meta["time_scale"] = "UTC"

    # Spetral resolution
    meta["spectral_range_min"] = int(100e6)
    meta["spectral_range_max"] = int(500e6)
    meta["spectral_resolution_min"] = 1631e3  # f/df
    meta["spectral_resolution_max"] = 8197e3  # f/df

    meta["spectral_sampling_step_min"] = (
        61e3  # frequency between 2 successive measurements
    )
    meta["spectral_sampling_step_max"] = (
        61e3  # frequency between 2 successive measurements
    )
    meta["spectral_bandwith_min"] = 61e3  # bandwidth of 1 MHz
    meta["spectral_bandwith_max"] = 61e3  # bandwidth of 1 MHz

    # Access
    meta["access_format"] = "application/fits"

    meta["bib_reference"] = "10.1007/s11207-011-9919-y"

    return meta


# Use in terminal python create_amateras_high08_metadata.py FOLDER_data folder_metadata
# can also give a single data file instead of folder_data
if __name__ == "__main__":
    (folder_FITS_path, folder_metadata_path,
        create_csv, create_json) = verify_input_paths(sys.argv, defaults='high16')

    if create_csv is False and create_json is False:
        print('Select one of the output return')
        exit()

    if create_csv:
        csv_filename = folder_metadata_path / "IPRT_high16_metadata_table.csv"
    else:
        csv_filename = folder_metadata_path / "empty"

    browse_save(folder_FITS_path, folder_metadata_path,
                csv_filename, create_high16_metadata, create_json, create_csv)
    print("Finished")
