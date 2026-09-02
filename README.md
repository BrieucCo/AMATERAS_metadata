# AMATERAS_metadata

Python tools to generate **metadata** for [VESPA tap server](http://padc-tap-tohoku.obspm.fr/) (in [EPN-TAP](https://voparis-confluence.obspm.fr/pages/viewpage.action?pageId=13697132) format) for the solar radio observations recorded by [**AMATERAS**](https://pparc.gp.tohoku.ac.jp/research/iprt/)  (the Assembly of Metric-band Aperture TElescope and Real-time Analysis System), the wideband metric radio spectro-polarimeter on the **Iitate Planetary Radio Telescope (IPRT)** at the Iitate observatory (Tohoku University) in Fukushima prefecture, Japan.

The scripts read the headers of the **FITS** files produced by the instrument and extract the information needed (dates, spectral range, resolution, access paths, etc.) to build metadata records usable by a Virtual Observatory–type service.


## Repository contents

| File / folder | Description |
| --- | --- |
| `create_amateras_low_metadata.py` | Generates metadata for the **low-resolution** dataset (`low`). Also contains the shared functions (`verify_input_paths`, `browse_save`, `delete_empty_folders`) reused by the other scripts. |
| `create_amateras_high08_metadata.py` | Generates metadata for the **high-resolution 8-bit** dataset (`high08`). |
| `create_amateras_high16_metadata.py` | Generates metadata for the **high-resolution 16-bit** dataset (`high16`). |
| `fromjsontocsv.py` | Merges a set of per-file JSON metadata records into a single CSV table. |
| `metadata_template.csv` | Template listing all the metadata columns/keys used. |
| `examples/` | Sample FITS files used to test the scripts without needing access to the production data. |
| `lowmetadata/`, `high08metadata/`, `high16metadata/` | Output folders holding the already-generated metadata (JSON / CSV) for each dataset type. |

## Requirements

- Python 3
- [astropy](https://www.astropy.org/) (`fits`, `Time`)
- [alive-progress](https://pypi.org/project/alive-progress/) *(optional, shows a progress bar)*

```bash
pip install astropy alive-progress
```

## Usage

Each metadata-generation script can be run directly from the command line:

```bash
python create_amateras_low_metadata.py [fits_folder] [metadata_folder] [create_csv] [create_json] [update]
```

- `fits_folder`: folder containing the `.fits` files to process (or a single file). If omitted, a default path is used depending on the script (e.g. `/db/IPRT-SUN/DATA2/` for `low`, `/db/IPRT-SUN/l1/high08/` for `high08`, `/db/IPRT-SUN/l1/high16/` for `high16`).
- `metadata_folder`: output folder for the metadata (defaults to `./lowmetadata/`, `./high08metadata/` or `./high16metadata/`).
- `create_csv` (0/1): whether to generate a summary CSV file (default: `1`).
- `create_json` (0/1): whether to generate a per-FITS-file JSON metadata file (default: `0`).
- `update` (0/1): only process FITS files not already present in the existing CSV, instead of rebuilding the whole table (default: `1`).

ℹ️ The `multiprocess` parameter (enabled by default) speeds up processing by parallelizing FITS file reading, but it is currently **incompatible with JSON generation** (`create_json=1`): combining both fold back on setting `multiprocess=False` to get the individual JSON files. This might result in a longer computation time.

### Examples

**Recommended use for IPRT server** to update csv files in default folder (e.g. `/db/IPRT-SUN/DATA2/` for `low`, `/db/IPRT-SUN/l1/high08/` for `high08`, `/db/IPRT-SUN/l1/high16/` for `high16`):
```bash
python create_amateras_low_metadata.py
python create_amateras_high16_metadata.py
python create_amateras_high08_metadata.py
```


Generate low-resolution metadata from the provided example folder:

```bash
python create_amateras_low_metadata.py ./examples/low/ ./lowmetadata/
```

Generate only a CSV (no JSON) for the high-resolution 8-bit dataset:

```bash
python create_amateras_high08_metadata.py ./examples/high08/ ./high08metadata/ 1 0
```

Rebuild a CSV from already-generated JSON files:

```bash
python fromjsontocsv.py ./lowmetadata/ ./lowmetadata.csv
```



## Generated metadata

The metadata follows the EPN-TAP standard.

The full list of keys is available in `metadata_template.csv`.

## Notes

The computational time for the update of high 16 is expected to be long (>30 min) due to the large number of files.
