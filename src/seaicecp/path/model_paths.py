import os
import glob
import warnings
from datetime import datetime

from seaicecp.verify import verify_path

def get_model_path(
    source_id: str,
    data_dir: str = '/seaicecp_data/bergybits/data',
    project: str = 'CMIP6',
    activity_id: str = 'HighResMIP',
):
    """ Find the file path for the specified model.

        Search the data directory that has been populated by `esgpull` for a model's `source_id` and return the file path.
        This assumes the `esgpull` convention of subdirectories: `data/project/activity_id/institution_id/source_id`.

        Parameters
        ----------
        source_id : `str`
            The name of the source ID (model) for which to find the file path.
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

        Returns
        -------
        model_filepaths : List of `str`
            A list of the file path(s) for the specified model.
        
        Examples
        --------
        >>> from seaicecp.path.find_data import get_model_path
        >>> get_model_path(source_id='AWI-CM-1-1-HR')
        ['/seaicecp_data/bergybits/data/CMIP6/HighResMIP/AWI/AWI-CM-1-1-HR']
        >>> get_model_path('HadGEM3-GC31-HM')
        ['/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-HM', '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/NERC/HadGEM3-GC31-HM']
    """
    # Verify input arguments
    if not isinstance(source_id, (str, type(None))):
        raise TypeError(f"(get_model_path) `source_id` must be a string. Got type: {type(source_id)}")
    if not isinstance(data_dir, str):
        raise TypeError(f"(get_model_path) `data_dir` must be a string. Got type: {type(data_dir)}")
    if not isinstance(project, str):
        raise TypeError(f"(get_model_path) `project` must be a string. Got type: {type(project)}")
    if not isinstance(activity_id, str):
        raise TypeError(f"(get_model_path) `activity_id` must be a string. Got type: {type(activity_id)}")
    # Assemble the full file path
    full_path = f"{data_dir}/{project}/{activity_id}"
    # Verify this full path exists
    full_path = verify_path(full_path)

    model_filepaths = []
    # Use glob to get a file path list down to the `source_id` depth
    source_id_filepaths = glob.glob(f"{full_path}/*/*")
    # Loop over those file paths to find which has the specified model
    for source_id_filepath in source_id_filepaths:
        # Check whether that file path ends in the specified model
        if source_id_filepath.endswith(source_id):
            model_filepaths.append(source_id_filepath)
    if len(model_filepaths) > 0:
        return model_filepaths
    
    # If no `source_id_filepath` was returned, get list of available model names and raise an error
    model_names = list_available_models(
        data_dir=data_dir,
        project=project,
        activity_id=activity_id,
    )
    raise FileNotFoundError(f"(get_model_path) Model with `source_id` {source_id} not found. Available `source_id`s: {model_names}")

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
