import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime

import seaicecp.params as sps
from seaicecp.verify import verify_path

def plot_time_series(
    dataset: (str, xr.DataArray, xr.Dataset),
    variable_id: str = None,
    plt_title: str = None,
    xlims: [str, str] = None,
    ylims: [float, float] = None,
    save_as: str = None,
    test: bool = False,
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
        xlims : List of `float`, optional
            The limits to use for the x-axis on the plot in the following format:
                - [x_min, x_max]

            where `x_min` and `x_max` are strings in the format `YYYY-MM-DD`
            Default is `None`, which expands the x-axis to include all the data.
        ylims : List of `float`, optional
            The limits to use for the y-axis on the plot in the following format:
                - [y_min, y_max]
                
            Default is `None`, which expands the y-axis to include all the data.
        save_as : `str`, `None`, optional
            The name of the file to which to save the plot.
            Default is `None`, which doesn't save the plot to a file.
        test : `bool`, optional
            If `True`, the function exists before making a plot for use in testing.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `xr.DataArray.plot()`.

        Returns
        -------
        If `test` == `False`: 
            `None`
        If `test` == `True` : 
            dataset : `xarray.DataArray`
        
        Examples
        --------
        >>> from seaicecp.dataset.field_mean import get_field_mean 
        >>> fldmean_xr = get_field_mean('example_siconc_dataset.nc')
        >>> from seaicecp.plot.time_series import plot_time_series
        >>> plot_time_series(dataset = fldmean_xr, variable_id = 'siconc')
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
    if isinstance(xlims, type([])):
        if not len(xlims) == 2:
            raise ValueError(f"(plot_time_series) `xlims` must have a length of 2. Got length: {len(xlims)}")
        else: 
            for i in range(len(xlims)):
                if not isinstance(xlims[i], (str)):
                    raise TypeError(f"(plot_time_series) `xlims[{i}]` must be a string. Got type: {type(xlims[i])}")
                else:
                    try:
                        xlims[i] = datetime.strptime(xlims[i], "%Y-%m-%d")
                    except ValueError as e:
                        raise ValueError(f"(plot_time_series) `xlims[{i}]` must be a date in the format `YYYY-MM-DD`. Got: {xlims[i]}")
    elif not isinstance(xlims, type(None)):
        raise TypeError(f"(plot_time_series) `xlims` must be a list or `None`. Got type: {type(xlims)}")
    if isinstance(ylims, type([])):
        if not len(ylims) == 2:
            raise ValueError(f"(plot_time_series) `ylims` must have a length of 2. Got length: {len(ylims)}")
        else: 
            for i in range(len(ylims)):
                if not isinstance(ylims[i], (int, float)):
                    raise TypeError(f"(plot_time_series) `ylims[{i}]` must be a number. Got type: {type(ylims[i])}")
    elif not isinstance(ylims, type(None)):
        raise TypeError(f"(plot_time_series) `ylims` must be a list or `None`. Got type: {type(ylims)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(plot_time_series) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.png' in save_as:
        raise TypeError(f"(plot_time_series) `save_as` must be a `.png` filepath. Got: {save_as}")
    if not isinstance(test, (type(True))):
        raise TypeError(f"(plot_time_series) `test` must be a `bool`. Got type: {type(test)}")
    
    # Information to output
    print(f"(plot_time_series) `save_as`: {save_as}")

    # Get limits for the y-axis
    if isinstance(ylims, type(None)):
        # Check whether the given variable is in the sea ice variable dictionary
        if variable_id in sps.sea_ice_vars.keys():
            # Check whether that variable has a plot range defined
            if 'plot_range' in sps.sea_ice_vars[variable_id].keys():
                ylims = sps.sea_ice_vars[variable_id]['plot_range']

    # Get the data array to plot
    if isinstance(dataset, xr.Dataset):
        dataset = dataset[variable_id]

    # If testing, exit before making the plot
    if test == True:
        return dataset

    # Plot the time series
    dataset.plot(
        xlim = xlims,
        ylim = ylims,
        **kwargs,
    )
    # Modify the plot
    plt.title(plt_title)

    return None