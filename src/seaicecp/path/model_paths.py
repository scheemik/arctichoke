import os
import glob
import warnings
from datetime import datetime

from arctichoke.verify import verify_path

def list_available_models(
    data_dir: str = '/arctichoke_data/bergybits/data',
    project: str = 'CMIP6',
    activity_id: str = 'HighResMIP',
    institution_id: (str, [str]) = None,
):
    """ List the names of the models available alphabetically.

        Search the data directory that has been populated by `esgpull` and return a list of all the available models, or `source_id`'s.
        This assumes the `esgpull` convention of subdirectories: `data/project/activity_id/institution_id/source_id`.

        Parameters
        ----------
        data_dir : `str`, optional
            The absolute file path to the data directory.
            The `esgpull` convention means this should end in `/data`.
            Default is `/arctichoke_data/bergybits/data`.
        project : `str`, optional
            The name of the project in which to search for available models.
            Default is `CMIP6`.
        activity_id : `str`, optional
            The name of the activity ID in which to search for available models.
            Default is `HighResMIP`.
        institution_id : `str`, list of `str`, or `None`, optional
            The name(s) of the institution ID(s) in which to search for available models.
            If `None` is given, all available institutions are included.
            Default is `None`.

        Returns
        -------
        model_names : List of `str`
            A list, sorted alphabetically, of the names of the available models.
        
        Examples
        --------
        >>> from arctichoke.path.find_data import list_available_models 
        >>> list_available_models()
        ['AWI/AWI-CM-1-1-HR', 'AWI/AWI-CM-1-1-LR', 'BCC/BCC-CSM2-HR', 'EC-Earth-Consortium/EC-Earth3P', 'EC-Earth-Consortium/EC-Earth3P-HR', 'MOHC/HadGEM3-GC31-HH', 'MOHC/HadGEM3-GC31-HM', 'MOHC/HadGEM3-GC31-LL', 'MOHC/HadGEM3-GC31-MM', 'NCAR/CESM1-CAM5-SE-HR', 'NCAR/CESM1-CAM5-SE-LR', 'NERC/HadGEM3-GC31-HH', 'NERC/HadGEM3-GC31-HM']
        >>> list_available_models(institution_id = 'EC-Earth-Consortium')
        ['EC-Earth-Consortium/EC-Earth3P', 'EC-Earth-Consortium/EC-Earth3P-HR']
        >>> list_available_models(institution_id = 'MOHC')
        ['MOHC/HadGEM3-GC31-HH', 'MOHC/HadGEM3-GC31-HM', 'MOHC/HadGEM3-GC31-LL', 'MOHC/HadGEM3-GC31-MM']
        >>> list_available_models(institution_id = ['MOHC', 'NERC'])
        ['MOHC/HadGEM3-GC31-HH', 'MOHC/HadGEM3-GC31-HM', 'MOHC/HadGEM3-GC31-LL', 'MOHC/HadGEM3-GC31-MM', 'NERC/HadGEM3-GC31-HH', 'NERC/HadGEM3-GC31-HM']
    """
    # Verify input arguments
    if not isinstance(data_dir, str):
        raise TypeError(f"(list_available_models) `data_dir` must be a string. Got type: {type(data_dir)}")
    if not isinstance(project, str):
        raise TypeError(f"(list_available_models) `project` must be a string. Got type: {type(project)}")
    if not isinstance(activity_id, str):
        raise TypeError(f"(list_available_models) `activity_id` must be a string. Got type: {type(activity_id)}")
    if isinstance(institution_id, type([])):
        for this_institution_id in institution_id:
            if not isinstance(this_institution_id, str):
                raise TypeError(f"(list_available_models) Each `institution_id` must be a string. Got type: {type(this_institution_id)}")
    elif not isinstance(institution_id, (str, type(None))):
        raise TypeError(f"(list_available_models) `institution_id` must be a string or `None`. Got type: {type(institution_id)}")
    # Assemble the full file path
    full_path = f"{data_dir}/{project}/{activity_id}"
    # Verify this full path exists
    full_path = verify_path(full_path)

    # Get the institution ID's 
    if isinstance(institution_id, type(None)):
        institution_ids = next(os.walk(full_path))[1]
    elif isinstance(institution_id, str):
        institution_ids = [institution_id]
    else:
        institution_ids = institution_id

    model_names = []
    # Loop through each institution ID
    for this_institution_id in institution_ids:
        # Verify the institution file path exists
        this_institution_path = verify_path(f"{full_path}/{this_institution_id}")
        # Loop across each model for that institution
        for this_model in next(os.walk(this_institution_path))[1]:
            # Verify the model path
            verify_path(f"{this_institution_path}/{this_model}")
            # Add this model to the list
            model_names.append(f"{this_institution_id}/{this_model}")

    return sorted(model_names)

def get_model_path(
    source_id: str,
    data_dir: str = '/arctichoke_data/bergybits/data',
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
            Default is `/arctichoke_data/bergybits/data`.
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
        >>> from arctichoke.path.find_data import get_model_path
        >>> get_model_path(source_id='AWI-CM-1-1-HR')
        ['/arctichoke_data/bergybits/data/CMIP6/HighResMIP/AWI/AWI-CM-1-1-HR']
        >>> get_model_path('HadGEM3-GC31-HM')
        ['/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-HM', '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/NERC/HadGEM3-GC31-HM']
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
