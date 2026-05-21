import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.cm as mplcm 
import matplotlib.colors as mplclrs
import numpy as np
from datetime import datetime

import seaicecp.params as sps
from seaicecp.verify import verify_path

def plot_seasonal_cycle(
    dataset: (str, xr.DataArray, xr.Dataset),
    variable_id: str = None,
    take_mean: bool = False,
    plt_title: str = None,
    xlims: [str, str] = None,
    ylims: [float, float] = None,
    c_map: [mplclrs.ListedColormap] = mplcm.viridis_r,
    save_as: str = None,
    test: bool = False,
    **kwargs,
):
    """ Plot a seasonal cycle of the dataset.

        Plots a seasonal cycle of the given dataset for the given variable, if applicable.

        Parameters
        ----------
        dataset : `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset for which to make a plot.
        variable_id : `str`
            The name of the variable ID to plot.
        take_mean : `bool`, optional
            Whether to take the mean for each month across all the years.
            Default is `False`.
        plt_title : `str`, `None`, optional
            The title to use for the plot.
            Default is `None`, which uses a default title for the plot.
        xlims : List of `float`, optional
            The limits to use for the x-axis on the plot in the following format:
                [x_min, x_max]
            where `x_min` and `x_max` are strings in the format `YYYY-MM-DD`
            Default is `None`, which expands the x-axis to include all the data.
        ylims : List of `float`, optional
            The limits to use for the y-axis on the plot in the following format:
                [y_min, y_max]
            Default is `None`, which expands the y-axis to include all the data.
        c_map : `matplotlib.colors.ListedColormap`, optional
            The color map to use for the different lines so their order is clearer.
            Default is `matplotlib.cm.viridis_r`, the reverse of `viridis`.
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
        >>> from seaicecp.plot.seasonal_cycle import plot_seasonal_cycle
        >>> plot_seasonal_cycle(dataset = fldmean_xr, variable_id = 'siconc')
    """
    # Verify input arguments
    if not isinstance(dataset, (str, xr.Dataset, xr.DataArray)):
        raise TypeError(f"(plot_seasonal_cycle) `dataset` must be a string, `xr.Dataset`, or `xr.DataArray`. Got type: {type(dataset)}")
    if isinstance(dataset, str):
        # Verify this is a valid path
        dataset = verify_path(dataset)
        if not dataset.endswith('.nc'):
            raise TypeError(f"(plot_seasonal_cycle) `dataset` must be a `.nc` filepath. Got: {dataset}")
    if not isinstance(variable_id, (str, type(None))):
        raise TypeError(f"(plot_seasonal_cycle) `variable_id` must be a string or `None`. Got type: {type(variable_id)}")
    if isinstance(variable_id, type(None)):
        if isinstance(dataset, xr.Dataset):
            raise ValueError(f"(plot_seasonal_cycle) `variable_id` must be a string if `dataset` is `xr.Dataset`. Got type: {type(variable_id)}")
        else:
            variable_id = dataset.name
    if isinstance(plt_title, type(None)):
        plt_title = f"Seasonal cycle of '{variable_id}'"
    elif not isinstance(plt_title, str):
        raise TypeError(f"(plot_seasonal_cycle) `plt_title` must be a string or `None`. Got type: {type(plt_title)}")
    if isinstance(xlims, type([])):
        if not len(xlims) == 2:
            raise ValueError(f"(plot_seasonal_cycle) `xlims` must have a length of 2. Got length: {len(xlims)}")
        else: 
            for i in range(len(xlims)):
                if not isinstance(xlims[i], (str)):
                    raise TypeError(f"(plot_seasonal_cycle) `xlims[{i}]` must be a string. Got type: {type(xlims[i])}")
                else:
                    try:
                        xlims[i] = datetime.strptime(xlims[i], "%Y-%m-%d")
                    except ValueError as e:
                        raise ValueError(f"(plot_seasonal_cycle) `xlims[{i}]` must be a date in the format `YYYY-MM-DD`. Got: {xlims[i]}")
    elif not isinstance(xlims, type(None)):
        raise TypeError(f"(plot_seasonal_cycle) `xlims` must be a list or `None`. Got type: {type(xlims)}")
    if isinstance(ylims, type([])):
        if not len(ylims) == 2:
            raise ValueError(f"(plot_seasonal_cycle) `ylims` must have a length of 2. Got length: {len(ylims)}")
        else: 
            for i in range(len(ylims)):
                if not isinstance(ylims[i], (int, float)):
                    raise TypeError(f"(plot_seasonal_cycle) `ylims[{i}]` must be a number. Got type: {type(ylims[i])}")
    elif not isinstance(ylims, type(None)):
        raise TypeError(f"(plot_seasonal_cycle) `ylims` must be a list or `None`. Got type: {type(ylims)}")
    if not isinstance(c_map, mplclrs.ListedColormap):
        raise TypeError(f"(plot_seasonal_cycle) `c_map` must be a `matplotlib.colors.ListedColormap`. Got type: {type(c_map)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(plot_seasonal_cycle) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.png' in save_as:
        raise TypeError(f"(plot_seasonal_cycle) `save_as` must be a `.png` filepath. Got: {save_as}")
    if not isinstance(test, (type(True))):
        raise TypeError(f"(plot_seasonal_cycle) `test` must be a `bool`. Got type: {type(test)}")
    
    # Information to output
    print(f"(plot_seasonal_cycle) `save_as`: {save_as}")

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
    
    # Convert the data array into a data frame
    ## Using `.isel` to select the first index of the `lat` and `lon` coordinates
    ## so that these are dropped. It is assumed that the dataset coming in to this function
    ## is a field mean, so there should only be one `lat` and one `lon` value
    data_frame = data_frame = dataset.isel(lat=0, lon=0).reset_coords(drop=True).to_dataframe()
    # Separate 'Year' and 'Month' from the time index
    data_frame['Month'] = data_frame.index.month
    data_frame['Year'] = data_frame.index.year 
    # Group the data by month of year and re-order the data frame into a shape that is easily plotted
    ## Using `.mean()` turns the DataFrameGroupBy object into a pandas.DataFrame 
    ## Using `.unstack()` re-orders the DataFrame into a table with rows for each year and columns for each month
    ## Using `.T` transposes the table to have rows for each month and columns for each year
    ## Using `.droplevel(0)` drops the unnecessary variable level and allows for the x-axis to be solely the month number
    data_frame = data_frame.groupby(['Year', 'Month']).mean().unstack().T.droplevel(0)
    # Take the mean for each month across the years, if applicable
    if take_mean == True:
        data_frame = data_frame.mean(axis=1)
        plt_title = f"Mean {plt_title}"

    # Get the values of the years in the data frame to set the line colors
    try:
        year_values = np.array(data_frame.columns)
    except:
        year_values = [np.nan]
    if len(year_values) > 2:
        # Create the normalizer based on the maximum and minimum year values
        norm = mplclrs.Normalize(vmin=year_values.min(), vmax=year_values.max())
        # Create the colormapper for the lines
        cmapper = mplcm.ScalarMappable(norm=norm, cmap=c_map)
        cmapper_to_plot = cmapper.to_rgba(year_values)
    else: 
        cmapper_to_plot = None

    # If testing, exit before making the plot
    if test == True:
        return data_frame

    # Plot the seasonal cycle
    this_ax = data_frame.plot(
        color=cmapper_to_plot,
        xlim = xlims,
        ylim = ylims,
        **kwargs,
    )
    # Modify the plot
    plt.title(plt_title)
    # If there are more than 10 lines, remove the legend and replace with a colorbar
    if len(year_values) > 10:
        this_ax.get_legend().remove()
        plt.colorbar(cmapper, ax=this_ax)

    return None