import os
import glob
import warnings
from datetime import datetime

from arctichoke.verify import verify_path
from arctichoke.path.variable_paths import get_variable_path

"""
The functions in this module assume the files are organized in the default fashion of `esgpull`.
This has the general structure as shown below.

/arctichoke_data/bergybits/
    ├── data
    │   └── CMIP6
    │       └── HighResMIP
    │           ├── AWI
    │           │   ├── AWI-CM-1-1-HR
    │           │   │   ├── hist-1950
    │           │   │   │   └── r1i1p1f2
    │           │   │   │       └── Ofx
    │           │   │   │           └── areacello
    │           │   │   │               └── gn
    │           │   │   │                   └── v20170825
    │           │   │   │                       └── areacello_Ofx_AWI-CM-1-1-HR_hist-1950_r1i1p1f2_gn.nc
    │           │   └── AWI-CM-1-1-LR
    │           │       ├── ...
    │           ├── ...
    │           ├── EC-Earth-Consortium
    │           │   ├── EC-Earth3P
    │           │   │   └── ...
    │           │   └── EC-Earth3P-HR
    │           │       └── hist-1950
    │           │           ├── r1i1p2f1
    │           │           │   └── SImon
    │           │           │       ├── siage
    │           │           │       │   └── gn
    │           │           │       │       └── v20181212
    │           │           │       │           ├── siage_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc
    │           │           │       │           ├── ...
    │           │           │       │           └── siage_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc
    │           │           │       ├── siconc
    │           │           │       │   └── gn
    │           │           │       │       └── v20181212
    │           │           │       │           ├── siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195201-195212.nc
    │           │           │       │           ├── ...
    │           │           │       │           └── siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc
    │           │           │       ├── sithick
    │           │           │       │   └── gn
    │           │           │       │       └── v20181212
    │           │           │       │           ├── sithick_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc
    │           │           │       │           ├── ...
    │           │           │       │           └── sithick_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc
    │           │           │       ├── siu
    │           │           │       │   └── gn
    │           │           │       │       └── v20181212
    │           │           │       │           ├── siu_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc
    │           │           │       │           ├── ...
    │           │           │       │           └── siu_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc
    │           │           │       └── siv
    │           │           │           └── gn
    │           │           │               └── v20181212
    │           │           │                   ├── siv_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc
    │           │           │                   ├── ...
    │           │           │                   └── siv_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc
    │           │           ├── r2i1p2f1
    │           │           │   └── SImon
    │           │           │       ├── ...
    │           │           └── r3i1p2f1
    │           │               └── SImon
    │           │                   ├── ...
    │           ├── MOHC
    │           │   ├── HadGEM3-GC31-HM
    │           │   │   └── ...
    │           │   ├── HadGEM3-GC31-LL
    │           │   │   └── ...
    │           │   └── HadGEM3-GC31-MM
    │           │       └── ...
    │           └── ...

"""

def list_variable_files(
    source_id: str,
    variable_id: str,
    with_modification: str = None,
    verbose: bool = False,
    **kwargs,
):
    """ Get a list of data files for the specified variable for the specified model.

        Search for all the files for the given model and variable and return them in a list.
        This assumes the `esgpull` convention of subdirectories: `data/project/activity_id/institution_id/source_id/experiment_id/variant_label/table_id/variable_id/gn/version/data_file.nc`.

        Parameters
        ----------
        source_id : `str`
            The name of the source ID (model) for which to get the variable files.
        variable_id : `str`
            The name of the variable ID for which to get the variable files.
        with_modification : `str`, `None`, optional
            The prefix of a modification to the data files to find.
            Ex: `trim_NWP_`.
            If `None`, returns only the original files.
            Default is `None`.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `get_variable_path()`.

        Returns
        -------
        data_filepaths : List of `str`
            A list, sorted alphabetically, of the filepaths of the variable data files.
        
        Examples
        --------
        >>> from arctichoke.path.find import list_variable_files
        >>> list_variable_files(source_id = 'HadGEM3-GC31-HM', variable_id = 'areacello')
        ['/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-HM/hist-1950/r1i1p1f1/Ofx/areacello/gn/v20190301/areacello_Ofx_HadGEM3-GC31-HM_hist-1950_r1i1p1f1_gn.nc']
        >>> list_variable_files(source_id = 'EC-Earth3P-HR', variable_id = 'siage')
        /workspace/src/arctichoke/path/find_data.py:399: UserWarning: (get_variable_path) More than one file path found: ['/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siage', '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r2i1p2f1/SImon/siage', '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/siage']
        Returning first result in list.
        ['/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siage/gn/v20181212/siage_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc',
        ...
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siage/gn/v20181212/siage_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc']
    """
    # Verify input arguments
    if not isinstance(source_id, (str, type(None))):
        raise TypeError(f"(list_variable_files) `source_id` must be a string. Got type: {type(source_id)}")
    if not isinstance(variable_id, str):
        raise TypeError(f"(list_variable_files) `variable_id` must be a string. Got type: {type(variable_id)}")
    if isinstance(with_modification, str):
        if not with_modification.endswith("_"):
            # Make sure the modificatin prefix ends with an underscore
            with_modification = f"{with_modification}_"
    elif not isinstance(with_modification, type(None)):
        raise TypeError(f"(list_variable_files) `with_modification` must be a string or `None`. Got type: {type(with_modification)}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(list_variable_files) `verbose` must be a `bool``. Got type: {type(verbose)}")

    # Get the path to the variable directory
    variable_path = get_variable_path(
        source_id = source_id,
        variable_id = variable_id,
        **kwargs,
    )

    # Use glob to get a file path list down to the `data_file` depth
    data_filepaths = glob.glob(f"{variable_path}/*/*/*")

    # Filter files based on modification
    if isinstance(with_modification, type(None)):
        # Filter out files with any modification prefixes
        data_filepaths = [item for item in data_filepaths if not 'trim' in item]
    else:
        # Filter to just files with the modification prefix
        data_filepaths = [item for item in data_filepaths if with_modification in item]
    if verbose:
        print(f"(list_variable_files) Found {len(data_filepaths)} files.")

    return sorted(data_filepaths)

def select_files_by_time(
    data_filepaths: [str],
    start: (str, int),
    end: (str, int),
    test: bool = False,
):
    """ Filter the list to be only the files in the given date range. 

        From the given list of datafiles, find the ones that are in between the given start and end dates and return those in a list.
        If the start and end are given as years, the returned list will include both the start and end years, if available.

        Parameters
        ----------
        data_filepaths : List of `str`
            A list, sorted alphabetically, of the filepaths of the variable data files.
        start : `str`, `int`
            The start date of the time range, either a string in the format `YYYY-MM-DD` or an integer of a year.
        end : `str`, `int`
            The end date of the time range, either a string in the format `YYYY-MM-DD` or an integer of a year.
        test : `bool`, optional
            If `True`, the function skips verifying the `data_filepaths` exist for use in testing.
            Default is `False`.

        Returns
        -------
        data_filepaths : List of `str`
            A list, sorted alphabetically, of the filepaths in the date range.
        
        Examples
        --------
        >>> from arctichoke.path.find import select_files_by_time
        >>> select_files_by_time(source_id = 'HadGEM3-GC31-HM', variable_id = 'areacello')
        ['/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-HM/hist-1950/r1i1p1f1/Ofx/areacello/gn/v20190301/areacello_Ofx_HadGEM3-GC31-HM_hist-1950_r1i1p1f1_gn.nc']
    """
    # Verify input arguments
    if not isinstance(data_filepaths, type([])):
        raise TypeError(f"(select_files_by_time) `data_filepaths` must be a list. Got type: {type(data_filepaths)}")
    else:
        for filepath in data_filepaths:
            if isinstance(filepath, str):
                # Verify this is a valid path
                if test == False:
                    filepath = verify_path(filepath)
                if not filepath.endswith('.nc'):
                    raise ValueError(f"(select_files_by_time) `filepath` must be a `.nc` filepath. Got: {filepath}")
            else:
                raise TypeError(f"(select_files_by_time) `filepath` must be a string. Got type: {type(filepath)}")
    if isinstance(start, str):
        try:
            # Check that the date follows the expected format
            foo = datetime.strptime(start, "%Y-%m-%d")
            # Get just the year from that date
            start = foo.year
        except ValueError as e:
            raise ValueError(f"(select_files_by_time) `start` must be a date in the format `YYYY-MM-DD`. Got: {start}")
    if isinstance(start, int):
        if start < 1950 or start > 3000:
            raise ValueError(f"(select_files_by_time) `start` must be between 1950 and 3000. Got: {start}")
    else:
        raise TypeError(f"(select_files_by_time) `start` must be a string or `int`. Got type: {type(start)}")
    if isinstance(end, str):
        try:
            # Check that the date follows the expected format
            foo = datetime.strptime(end, "%Y-%m-%d")
            # Get just the year from that date
            end = foo.year
        except ValueError as e:
            raise ValueError(f"(select_files_by_time) `end` must be a date in the format `YYYY-MM-DD`. Got: {end}")
    if isinstance(end, int):
        if end < 1950 or end > 3000:
            raise ValueError(f"(select_files_by_time) `end` must be between 1950 and 3000. Got: {end}")
    else:
        raise TypeError(f"(select_files_by_time) `end` must be a string or `int`. Got type: {type(end)}")
    if start > end:
        raise ValueError(f"(select_files_by_time) `start` must be before `end`. Got `start`: {start} and `end`: {end}")
    if not isinstance(test, (type(True))):
        raise TypeError(f"(select_files_by_time) `test` must be a `bool`. Got type: {type(test)}")

    data_filepaths_in_date_range = []
    # Check each file in the list
    for data_file in data_filepaths:
        # Get the year of the datafile, assuming the following naming convention:
        ## `...<experiment_id>_<variant_label>_gn_YYYYMM-YYYYMM.nc`
        file_years = data_file.split('_')[-1]
        start_year = int(file_years[0:4])
        end_year = int(file_years.split('-')[-1][0:4])
        # If the span of this file crosses the specified date range, include it in the list of files
        if start_year >= start and end_year <= end:
            data_filepaths_in_date_range.append(data_file)

    return sorted(data_filepaths_in_date_range)
