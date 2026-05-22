import xarray as xr
from cdo import Cdo
cdo = Cdo()
# Set path for temporary files in case of a crash
cdo = Cdo(tempdir='./cdo_tmp/')
cdo.cleanTempDir()

from seaicecp.verify import verify_path

def get_field_mean(
    dataset: (str, [str], xr.DataArray, xr.Dataset),
    save_as: str = None,
    **kwargs,
):
    """ Get the field mean of the dataset.

        Use the `cdo` function `fldmean` to take the field mean (the mean over the geographic area) of the given dataset.

        Parameters
        ----------
        dataset : `str`, list of `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset of which to take the field mean.
        save_as : `str`, `None`, optional
            The file name to pass to `cdo.fldmean(output=save_as)`.
            Default is `None`, which doesn't save the dataset to a file.
        **kwargs
            Keyword arguments to pass to `cdo.fldmean()`.

        Returns
        -------
        fldmean_xr : `xarray.Dataset`
            A dataset of the field mean of the input data.
        
        Examples
        --------
        >>> from seaicecp.dataset.field_mean import get_field_mean 
        >>> fldmean_xr = get_field_mean('data/NWP_cdo_CLI_areacello_Ofx_EC-Earth3P-HR_highres-future_r2i1p2f1_gn.nc')
        >>> fldmean_xr['areacello'].values[0]
        (get_field_mean) `save_as`: None
        array([1.3731426e+08], dtype=float32)
    """
    # Verify input arguments
    if isinstance(dataset, str):
        # Wrap that string into a list
        dataset = [dataset]
    if isinstance(dataset, (xr.Dataset, xr.DataArray)):
        input_command = dataset
        cdo_command = cdo.fldmean
    elif isinstance(dataset, type([])):
        if len(dataset) < 1:
            raise ValueError(f"(get_field_mean) `dataset` must have at least one item. Got: {dataset}")
        # Assemble the `cdo` input command
        input_command = "[ -fldmean :"
        for datafile in dataset:
            if not isinstance(datafile, str):
                raise TypeError(f"(get_field_mean) Each item in `dataset` list must be a string. Got: {type(datafile)}")
            # Verify this is a valid path
            datafile = verify_path(datafile)
            if not datafile.endswith('.nc'):
                raise TypeError(f"(plot_time_series) `datafile` must be a `.nc` filepath. Got: {datafile}")
            input_command = f"{input_command} {datafile}"
        input_command = f"{input_command} ]"
        print(f"(get_field_mean) `input`: {input_command}")
        cdo_command = cdo.mergetime
    else:
        raise TypeError(f"(get_field_mean) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(get_field_mean) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.nc' in save_as:
        raise TypeError(f"(get_field_mean) `save_as` must be a `.nc` filepath. Got: {save_as}")
    
    # Information to output
    print(f"(get_field_mean) `save_as`: {save_as}")

    # Use `cdo` to calculate the field mean
    fldmean_xr = cdo_command(
        input = input_command,
        returnXDataset = 'field_mean',
        output = save_as,
        **kwargs,
    )

    return fldmean_xr