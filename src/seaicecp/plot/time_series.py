import xarray as xr
import matplotlib.pyplot as plt

import seaicecp.params as sps
from seaicecp.verify import verify_path

def plot_time_series(
    dataset: (str, xr.DataArray, xr.Dataset),
    variable_id: str = None,
    plt_title: str = None,
    save_as: str = None,
    **kwargs,
):
    """ Plot a time series of the dataset.

        Plots a time series of the given dataset for the given variable, if applicable.

        Parameters
        ----------
        dataset : `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset for which to make a plot.
        variable_id : `str`
            The name of the variable ID to plot.
        plt_title : `str`, `None`, optional
            The title to use for the plot.
            Default is `None`, which uses a default title for the plot.
        save_as : `str`, `None`, optional
            The name of the file to which to save the plot.
            Default is `None`, which doesn't save the plot to a file.
        **kwargs
            Keyword arguments to pass to `xr.DataArray.plot()`.

        Returns
        -------
        None
        
        Examples
        --------
        >>> 
    """
    # Verify input arguments
    if not isinstance(dataset, (str, xr.Dataset, xr.DataArray)):
        raise TypeError(f"(plot_time_series) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if isinstance(dataset, str):
        # Verify this is a valid path
        dataset = verify_path(dataset)
        if not dataset.endswith('.nc'):
            raise TypeError(f"(plot_time_series) `dataset` must be a `.nc` filepath. Got: {dataset}")
    if not isinstance(variable_id, (str, type(None))):
        raise TypeError(f"(plot_time_series) `variable_id` must be a string or `None`. Got type: {type(variable_id)}")
    if isinstance(variable_id, type(None)):
        if isinstance(dataset, xr.Dataset):
            raise ValueError(f"(plot_time_series) `variable_id` must be a string if `dataset` is `xr.Dataset`. Got type: {type(variable_id)}")
        else:
            variable_id = dataset.name
    if isinstance(plt_title, type(None)):
        plt_title = f"Time series of '{variable_id}'"
    elif not isinstance(plt_title, str):
        raise TypeError(f"(plot_time_series) `plt_title` must be a string or `None`. Got type: {type(plt_title)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(plot_time_series) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.png' in save_as:
        raise TypeError(f"(plot_time_series) `save_as` must be a `.png` filepath. Got: {save_as}")
    
    # Information to output
    print(f"(plot_time_series) `save_as`: {save_as}")

    # Plot the time series
    if isinstance(dataset, xr.DataArray):
        dataset.plot()
    elif isinstance(dataset, xr.Dataset):
        dataset[variable_id].plot()
    else:
        raise ValueError(f"(plot_time_series) `dataset` was neither `xr.DataArray` nor `xr.Dataset`. Cannot plot `dataset` of type: {type(dataset)}")
    plt.title(plt_title)

    return None