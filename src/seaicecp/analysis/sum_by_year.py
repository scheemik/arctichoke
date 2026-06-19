import numpy as np
import xarray as xr

from seaicecp.dataset.get_variable import get_variable_name
from seaicecp.dataset.trim_dataset import trim_latlon
from seaicecp.path.manipulate_paths import make_file_path
import seaicecp.params as sps
from seaicecp.verify import verify_path

def sum_by_year(
    dataset: (str, [str], xr.DataArray, xr.Dataset),
    save_as: str = None,
    verbose: bool = False,
    **kwargs,
):
    """ Sum a dataset by year along the time axis.

        Groups the dataset by year and sums each year.
        This results in one time step for each year in the given dataset.

        Parameters
        ----------
        dataset : `str`, list of `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset of which to sum by year.
        save_as : `str`, `None`, optional
            The file name to which to save the modified dataset.
            Default is `None`, which doesn't save the dataset to a file.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `xr.sum()`.

        Returns
        -------
        year_summed_xr : `xarray.Dataset`
            A dataset where the data has been summed by year.
        
        Examples
        --------
        >>> from seaicecp.dataset.example_dataset import make_example_dataset
        >>> dataset = make_example_dataset(n=3, test_var_name='siconc')
        >>> dataset['siconc'].values
        array([[0., 1., 2.],
               [3., 4., 5.],
               [6., 7., 8.]])
        >>> from seaicecp.analysis.landfast import sum_by_year
        >>> dataset_sipacked = sum_by_year(dataset, packed_threshold=4)
        >>> dataset_sipacked['sipacked'].values
        array([[0., 0., 0.],
               [0., 1., 1.],
               [1., 1., 1.]])
    """
    # Verify input arguments
    if not isinstance(verbose, bool):
        raise TypeError(f"(sum_by_year) `verbose` must be a `bool`. Got type: {type(verbose)}")
    if isinstance(dataset, str):
        # Wrap that string into a list
        dataset = [dataset]
    if isinstance(dataset, type([])):
        if len(dataset) < 1:
            raise ValueError(f"(sum_by_year) `dataset` must have at least one item. Got: {dataset}")
        for datafile in dataset:
            if not isinstance(datafile, str):
                raise TypeError(f"(sum_by_year) Each item in `dataset` list must be a string. Got: {type(datafile)}")
            # Verify this is a valid path
            datafile = verify_path(datafile)
            if not datafile.endswith('.nc'):
                raise TypeError(f"(plot_time_series) `datafile` must be a `.nc` filepath. Got: {datafile}")
        # Load all the files at once
        if verbose:
            print(f"(sum_by_year) When passing a list of files, ensure their coordinates match as that is not verified in this function.")
        dataset = xr.open_mfdataset(dataset)
    elif not isinstance(dataset, (xr.Dataset, xr.DataArray)):
        raise TypeError(f"(sum_by_year) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(sum_by_year) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.nc' in save_as:
        raise TypeError(f"(sum_by_year) `save_as` must be a `.nc` filepath. Got: {save_as}")
    
    # Information to output
    if verbose:
        print(f"(sum_by_year) `save_as`: {save_as}")

    # Sum the dataset by year
    year_summed_xr = dataset.groupby('time.year').sum(dim='time')

    if isinstance(dataset, xr.Dataset):
        # Get the name of the variable in the dataset
        var_name = get_variable_name(year_summed_xr)
        # Rename the variable, giving it the suffix `_year_sum`
        year_summed_xr = year_summed_xr.rename_vars({var_name: f'{var_name}_year_sum'})

    # Save the trimmed dataset, if applicable
    if not isinstance(save_as, type(None)):
        # Save the plot to file
        year_summed_xr.to_netcdf(save_as)
    
    return year_summed_xr
