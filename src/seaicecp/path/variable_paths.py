import glob
import os
import warnings

from seaicecp.verify import verify_path
from seaicecp.path.model_paths import get_model_path, list_available_models

def list_available_variables(
    source_id: str,
    experiment_id: str = None,
    list_var_mods = False,
    **kwargs,
):
    """ List the names of the variables available for the specified model.

        Search the data directory that has been populated by `esgpull` and return a list of all the available varibles, or `variable_id`'s for the specified model.
        This assumes the `esgpull` convention of subdirectories: `data/project/activity_id/institution_id/source_id/experiment_id/variant_label/table_id/variable_id`.

        Parameters
        ----------
        source_id : `str`
            The name of the source ID (model) for which to find the variable paths.
        experiment_id : `str` or `None`, optional
            The name of the experiment ID in which to search for available variables.
            If `None` is given, all available experiments are included.
            Default is `None`.
        list_var_mods : `bool`, optional
            Whether to include information about modifications made to the datafiles.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `get_model_path()`.

        Returns
        -------
        avail_var_dict : `dict`
            A dictionary of experiment ID's whose keys are dictionaries of variant labels whose keys are lists of available variables.
        
        Examples
        --------
        >>> from seaicecp.path.find_data import list_available_variables 
        >>> list_available_variables(source_id = 'HadGEM3-GC31-HM')
        {'MOHC/HadGEM3-GC31-HM': {
            'control-1950': {
                'r1i1p1f1': ['areacello']},
            'highres-future': {
                'r1i1p1f1': ['areacello', 'siu', 'siv', 'sithick', 'siconc', 'siage'],
                'r1i3p1f1': ['siconc', 'siage', 'siv', 'sithick', 'siu']},
            'hist-1950': {
                'r1i1p1f1': ['areacello', 'siage', 'siv', 'siu', 'siconc', 'sithick'],
                'r1i3p1f1': ['siconc', 'sithick', 'siu', 'siage', 'siv']}},
        'NERC/HadGEM3-GC31-HM': {
            'highres-future': {
                'r1i2p1f1': ['siv', 'siu', 'siconc', 'sithick', 'siage']},
            'hist-1950': {
                'r1i2p1f1': ['siconc', 'siu', 'sithick', 'siv', 'siage']}}}
        >>> list_available_variables(source_id = 'HadGEM3-GC31-HM', experiment_id = 'hist-1950')
        {'MOHC/HadGEM3-GC31-HM': {
            'hist-1950': {
                'r1i1p1f1': ['areacello', 'siage', 'siv', 'siu', 'siconc', 'sithick'],
                'r1i3p1f1': ['siconc', 'sithick', 'siu', 'siage', 'siv']}},
        'NERC/HadGEM3-GC31-HM': {
            'hist-1950': {
                'r1i2p1f1': ['siconc', 'siu', 'sithick', 'siv', 'siage']}}}
    """
    # Verify input arguments
    if not isinstance(source_id, str):
        raise TypeError(f"(list_available_variables) `source_id` must be a string. Got type: {type(source_id)}")
    if not isinstance(experiment_id, (str, type(None))):
        raise TypeError(f"(list_available_variables) `experiment_id` must be a string or `None`. Got type: {type(experiment_id)}")
    if not isinstance(list_var_mods, bool):
        raise TypeError(f"(list_available_variables) `list_var_mods` must be a `bool`. Got type: {type(list_var_mods)}")
    
    # Get the path of the model
    model_paths = get_model_path(source_id, **kwargs)
    # Verify this model path exists
    for i in range(len(model_paths)):
        model_paths[i] = verify_path(model_paths[i])

    # Make a dictionary to store resulting available variables
    avail_var_dict = {f"{model_path.split('/')[-2]}/{model_path.split('/')[-1]}": None for model_path in sorted(model_paths)}

    # Loop across the model paths
    for model_path in model_paths:
        short_model_path = f"{model_path.split('/')[-2]}/{model_path.split('/')[-1]}"
        
        # Get the experiment ID's 
        if isinstance(experiment_id, type(None)):
            experiment_ids = next(os.walk(model_path))[1]
        else:
            experiment_ids = [experiment_id]
        
        # Make a dictionary to store resulting available variables
        avail_var_dict[short_model_path] = {experiment_id: None for experiment_id in sorted(experiment_ids)}

        # Get the variant labels (ensemble members) for each experiment ID
        for this_experiment_id in experiment_ids:
            # Verify the experiment ID path exists
            experiment_path = verify_path(f"{model_path}/{this_experiment_id}")
            # Get the variant labels
            variant_labels = next(os.walk(experiment_path))[1]
            # Add the variant labels as a dictionary to the available variable dictionary
            avail_var_dict[short_model_path][this_experiment_id] = {variant_label: [] for variant_label in sorted(variant_labels)}

            # Get the variables available for each variant label
            for variant_label in variant_labels:
                # Verify the variant path exists
                variant_path = verify_path(f"{experiment_path}/{variant_label}")
                # Get the table ID's
                table_ids = next(os.walk(variant_path))[1]
                # Get the variables available for each table ID
                table_paths = []
                for table_id in table_ids:
                    # Verify the table path exists and add it to the list of table paths
                    table_paths.append(verify_path(f"{variant_path}/{table_id}"))
                if list_var_mods == False:
                    # Get the variable names using nested iterations to avoid a list of lists
                    avail_var_dict[short_model_path][this_experiment_id][variant_label] = [var_name for path in table_paths for var_name in next(os.walk(path))[1]]
                else:
                    # Set up the dictionary to hold the table information
                    avail_var_dict[short_model_path][this_experiment_id][variant_label] = {table_id: None for table_id in table_ids}
                    # Loop across the table paths
                    for table_id in table_ids:
                        # Get the variable names
                        variable_ids = next(os.walk(f"{variant_path}/{table_id}"))[1]
                        # Set up the dictionary to hold the variable information
                        avail_var_dict[short_model_path][this_experiment_id][variant_label][table_id] = {variable_id: None for variable_id in variable_ids}
                        var_mod_dicts = []
                        for variable_id in variable_ids:
                            # Verify the variable path exists
                            variable_path = f"{variant_path}/{table_id}/{variable_id}"
                            # Get the dictionary list of modifications for this variable path
                            var_mod_dicts.append(list_variable_modifications(variable_path))
                            var_mod_dict = list_variable_modifications(variable_path)
                            # Add that dictionary of modifications to the variable dictionary
                            avail_var_dict[short_model_path][this_experiment_id][variant_label][table_id][variable_id] = var_mod_dict

    return avail_var_dict

def get_variable_path(
    source_id: str,
    variable_id: str,
    data_dir: str = '/seaicecp_data/bergybits/data',
    project: str = 'CMIP6',
    activity_id: str = 'HighResMIP',
    experiment_id: str = 'hist-1950',
    variant_label: str = None,
    **kwargs,
):
    """ Find the file path for the specified model and variable.

        Search the data directory that has been populated by `esgpull` for a model's `source_id` and return the file path.
        This assumes the `esgpull` convention of subdirectories: `data/project/activity_id/institution_id/source_id/experiment_id/variant_label/table_id/variable_id`.

        Parameters
        ----------
        source_id : `str`
            The name of the source ID (model) for which to find the variable path.
        variable_id : `str`
            The name of the variable ID for which to find the variable path.
        data_dir : `str`, optional
            The absolute file path to the data directory.
            The `esgpull` convention means this should end in `/data`.
            Default is `/seaicecp_data/bergybits/data`.
        project : `str`, optional
            The name of the project in which to search for available models.
            Default is `CMIP6`.
        activity_id : `str`, optional
            The name of the activity ID in which to search for available models.
            Default is `HighResMIP`.
        experiment_id : `str`, optional
            The name of the experiment ID in which to search for available variables.
            Default is `hist-1950`.
        variant_label : `str`, `None`, optional
            The name of the variant label (ensemble member) for which to get the variable path.
            If `None` is given, the file path for the first variant with the variable is returned.
            Default is `None`.
        **kwargs
            Keyword arguments to pass to `get_model_path()`.

        Returns
        -------
        variable_path : `str`
            The file path to the directory for the specified variable from the specified model.
        
        Examples
        --------
        >>> from seaicecp.path.find_data import get_variable_path
        >>> get_variable_path(source_id = 'HadGEM3-GC31-HM', variable_id = 'areacello')
        '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-HM/hist-1950/r1i1p1f1/Ofx/areacello'
        >>> get_variable_path(source_id = 'EC-Earth3P-HR', variable_id = 'siage')
        '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/siage'
        /workspace/src/seaicecp/path/find_data.py:396: UserWarning: (get_variable_path) More than one file path found: ['/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siage', '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r2i1p2f1/SImon/siage', '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/siage']
        Returning first result in list.
        '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siage'
        >>> get_variable_path(source_id = 'EC-Earth3P-HR', variable_id = 'siage', variant_label = 'r3i1p2f1')
        '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/siage'
    """
    # Verify input arguments
    if not isinstance(source_id, (str, type(None))):
        raise TypeError(f"(get_variable_path) `source_id` must be a string. Got type: {type(source_id)}")
    if not isinstance(variable_id, str):
        raise TypeError(f"(get_variable_path) `variable_id` must be a string. Got type: {type(variable_id)}")
    if not isinstance(data_dir, str):
        raise TypeError(f"(get_variable_path) `data_dir` must be a string. Got type: {type(data_dir)}")
    if not isinstance(project, str):
        raise TypeError(f"(get_variable_path) `project` must be a string. Got type: {type(project)}")
    if not isinstance(activity_id, str):
        raise TypeError(f"(get_variable_path) `activity_id` must be a string. Got type: {type(activity_id)}")
    if not isinstance(experiment_id, str):
        raise TypeError(f"(get_variable_path) `experiment_id` must be a string. Got type: {type(experiment_id)}")
    if not isinstance(variant_label, (str, type(None))):
        raise TypeError(f"(get_variable_path) `variant_label` must be a string or `None`. Got type: {type(variant_label)}")

    # Get the model path
    model_paths = get_model_path(
        source_id = source_id,
        data_dir = data_dir,
        project = project,
        activity_id = activity_id,
    )

    full_variable_id_filepath_list = []

    # Loop across model paths
    for model_path in model_paths:
        # Use glob to get a file path list down to the `variable_id` depth
        variable_id_filepaths = glob.glob(f"{model_path}/*/*/*/*")

        # Filter to just those with the specified variable ID
        variable_id_filepaths = [item for item in variable_id_filepaths if item.endswith(variable_id)]

        # Filter to just those with the specified experiment ID
        variable_id_filepaths = [item for item in variable_id_filepaths if experiment_id in item]

        # Filter to just those with the specified variant label, if applicable
        if not isinstance(variant_label, type(None)):
            variable_id_filepaths = [item for item in variable_id_filepaths if variant_label in item]
        
        # Add this list to the full list
        full_variable_id_filepath_list += variable_id_filepaths

    # Check how many file paths remain
    if len(full_variable_id_filepath_list) > 1:
        # There is more than one matching file path for the specified variable for the specified model
        warnings.warn(f"(get_variable_path) More than one file path found: {sorted(full_variable_id_filepath_list)}\nReturning first result in list.", UserWarning)
        # Return the first variant alphabetically
        return sorted(full_variable_id_filepath_list)[0]
    elif len(full_variable_id_filepath_list) == 0:
        # If no file paths had the variable in it, get the list of available variables and raise an error
        available_variables = list_available_variables(
            source_id = source_id,
            experiment_id = experiment_id,
            data_dir = data_dir,
            project = project,
            activity_id = activity_id,
        )
        raise ValueError(f"(get_variable_path) Variable {variable_id} not found for {source_id}. Available variables: {available_variables}")
    else:
        # If there is only one file path remaining, return it
        return full_variable_id_filepath_list[0]

def list_variable_modifications(
    variable_path: str,
    list_filenames: bool = False,
    verbose: bool = False,
):
    """ List the modifications made to variable files in the specified path.

        Search the given directory of data files and return a dictionary indicating whether any modifications have been made and how many files in each modification category exist.
        This assumes modifications are made to files by adding a prefix to the file name.

        Parameters
        ----------
        variable_path : `str`
            The filepath to the variable in question.
            Expected format: `data/project/activity_id/institution_id/source_id/experiment_id/variant_label/table_id/variable_id`.
        list_filenames : `bool`, optional
            Whether to list all the file names for each modification or to give the number of files.
            Default is `False`, which gives the number of files.
        verbose : `bool`, optional
            Whether to output additional information while the function is running.
            Default is `False`.

        Returns
        -------
        var_mod_dict : `dict`
            A dictionary of modification prefixes, the values of which are either the number of files under that modification or a list all the files under that modification.
        
        Examples
        --------
        >>> from seaicecp.path.find_data import list_variable_modifications 
        >>> list_variable_modifications(variable_path = '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/AWI/AWI-CM-1-1-HR/hist-1950/r1i1p1f2/Ofx/areacello', list_filenames = True)
        {'': ['areacello_Ofx_AWI-CM-1-1-HR_hist-1950_r1i1p1f2_gn.nc']}
        >>> list_variable_modifications(variable_path = '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r2i1p2f1/SImon/siconc')
        {'': 65, 'trim_NWP_': 65}
    """
    # Verify input arguments
    if not isinstance(variable_path, str):
        raise TypeError(f"(list_variable_modifications) `variable_path` must be a string. Got type: {type(variable_path)}")
    variable_path = verify_path(variable_path)

    # Get the variable name
    variable_id = variable_path.split('/')[-1]

    # Information to output
    if verbose == True:
        print(f"(list_variable_modifications) `variable_id`: {variable_id}")

    # Use glob to get a file path list down to the `data_file` depth
    data_filepaths = glob.glob(f"{variable_path}/*/*/*")

    # Filter to just netCDF files
    data_filepaths = [item for item in data_filepaths if '.nc' in item]
    if len(data_filepaths) < 1:
        raise FileNotFoundError(f"(list_variable_modifications) No `.nc` files found in `variable_path`: {variable_path}/*/*/*")
    
    # Get just the file names, removing the directory paths
    data_filepaths = [item.split('/')[-1] for item in data_filepaths]

    # Get just the modification prefixes, removing the file names
    modification_prefixes = [item.split(variable_id)[0] for item in data_filepaths]
    # Get just the unique prefixes
    modification_prefixes = list(set(modification_prefixes))
    # Make a dictionary to store resulting lists of files
    var_mod_dict = {mod_prefix: None for mod_prefix in sorted(modification_prefixes)}

    # For each modification prefix, get the list of relevant files
    for mod_prefix in modification_prefixes:
        # For modification prefixes, list the items which contain that prefix
        if mod_prefix != '':
            these_data_filepaths = [item for item in data_filepaths if item.startswith(mod_prefix)]
        # For unmodified files, use process of elimination
        else:
            # Make a list of all prefixes except for `''`
            temp_list = modification_prefixes.copy()
            temp_list.remove('')
            # If there are any prefixes left, loop through them
            if len(temp_list) > 0:
                these_data_filepaths = [item for item in data_filepaths if not item.startswith(temp_list[0])]
                for i in range(1, len(modification_prefixes)):
                    these_data_filepaths = [item for item in these_data_filepaths if not item.startswith(temp_list[0])]
            else:
                these_data_filepaths = data_filepaths
        if list_filenames:
            var_mod_dict[mod_prefix] = sorted(these_data_filepaths)
        else:
            var_mod_dict[mod_prefix] = len(these_data_filepaths)

    return var_mod_dict
