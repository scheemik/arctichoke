from datetime import datetime
from matplotlib.axes._axes import Axes
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from arctichoke.analysis import trend_in_time
from arctichoke.dataset import get_epoch_times
import arctichoke.params as sps
from arctichoke.plot.labels_and_titles import make_title, make_label
from arctichoke.verify import verify_path

def plot_time_series(
    dataset: (str, xr.DataArray, xr.Dataset),
    variable_id: str = None,
    add_regression: bool = False,
    reg_label: str = None,
    plt_title: str = None,
    y_ax_label: str = None,
    xlims: [str, str] = None,
    ylims: [float, float] = None,
    line_clr: str = None,
    line_style: str = '--',
    include_legend: bool = True,
    fig: Figure = None,
    axis: Axes = None,
    save_as: str = None,
    verbose: bool = False,
    test: bool = False,
    **kwargs,
):
    """ Plot a time series of the dataset.

        Plots a time series of the given dataset for the given variable, if applicable.

        Parameters
        ----------
        dataset : `str`, `xarray.DataArray`, `xarray.Dataset`
            The dataset for which to make a plot.
        variable_id : `str`, optional
            The name of the variable ID to plot.
        add_regression : `bool`, optional
            Whether to add a linear regression line to the plot.
            Default is `False`.
        reg_label : `str`, `None`, optional
            The label to use for the regression line.
            Note that this has no effect when `add_regression` is `False`.
            Default is `None`, which uses a default label, the equation of the regression line.
        plt_title : `str`, `None`, optional
            The title to use for the plot.
            Default is `None`, which uses a default title for the plot.
        y_ax_label : `str`, `None`, optional
            Specify the label of the plot's y-axis, if `None` is given, use the `make_label()` function to create the label.
            Default is `None`.
        xlims : List of `float`, optional
            The limits to use for the x-axis on the plot in the following format:
                - [x_min, x_max]

            where `x_min` and `x_max` are strings in the format `YYYY-MM-DD`
            Default is `None`, which expands the x-axis to include all the data.
        ylims : List of `float`, optional
            The limits to use for the y-axis on the plot in the following format:
                - [y_min, y_max]
                
            Default is `None`, which expands the y-axis to include all the data.
        line_clr: `str`, `None`, optional
            The color of line to use in the plot. 
            Default is `None` which uses the default `matplotlib` colors. 
        line_style : `str`, optional
            The style of line to use in the time series plot (not the regression line).
            Default is `:`. 
        include_legend : `bool`, optional
            Whether or not to add the legend to the axis.
            Default is `True`.
        fig : `None`, `matplotlib.figure.Figure`, optional
            If not `None`, this is the pre-existing figure on which to plot the map.
            Default is `None` which creates a new figure with a new axis.
        axis : `None`, `matplotlib.axes._axes.Axes`, optional
            If not `None`, this is the pre-existing axis in `fig` on which to plot the map.
            Default is `None` which creates a new figure with a new axis.
        save_as : `str`, `None`, optional
            The name of the file to which to save the plot.
            Default is `None`, which doesn't save the plot to a file.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        test : `bool`, optional
            If `True`, the function exists before making a plot for use in testing.
            Default is `False`.
        **kwargs
            Keyword arguments to pass to `xr.DataArray.plot()`.

        Returns
        -------
        If `test` == `False`: 
            time_series_axis : `matplotlib.axes._axes.Axes`
                The axis on which the time series has been plotted. 
        If `test` == `True` : 
            dataset : `xarray.DataArray`
                The dataset of the time series.
        
        Examples
        --------
        >>> from arctichoke.dataset.field_mean import get_field_mean 
        >>> fldmean_xr = get_field_mean('example_siconc_dataset.nc')
        >>> from arctichoke.plot.time_series import plot_time_series
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
    if not isinstance(add_regression, (type(True))):
        raise TypeError(f"(plot_time_series) `add_regression` must be a `bool`. Got type: {type(add_regression)}")
    if isinstance(reg_label, type(None)):
        reg_label = make_title(dataset)
    elif not isinstance(reg_label, str):
        raise TypeError(f"(plot_time_series) `reg_label` must be a string or `None`. Got type: {type(reg_label)}")
    if not isinstance(plt_title, (str, type(None))):
        raise TypeError(f"(plot_time_series) `plt_title` must be a string or `None`. Got type: {type(plt_title)}")
    if not isinstance(y_ax_label, (str, type(None))):
        raise TypeError(f"(plot_time_series) `y_ax_label` must be a string or `None`. Got type: {type(y_ax_label)}")
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
    if not isinstance(fig, (str, (type(None), Figure))):
        raise TypeError(f"(make_cartopy_map) `fig` must be `None` or `matplotlib.figure.Figure`. Got type: {type(fig)}")
    if not isinstance(axis, (str, (type(None), Axes))):
        raise TypeError(f"(make_cartopy_map) `axis` must be `None` or `matplotlib.axes._axes.Axes`. Got type: {type(axis)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(plot_time_series) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    if not isinstance(line_clr, (str, type(None))):
        raise TypeError(f"(plot_time_series) `line_clr` must be a string or `None`. Got type: {type(line_clr)}")
    elif isinstance(save_as, str) and not '.png' in save_as:
        raise TypeError(f"(plot_time_series) `save_as` must be a `.png` filepath. Got: {save_as}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(plot_time_series) `verbose` must be a `bool`. Got type: {type(verbose)}")
    if not isinstance(test, (type(True))):
        raise TypeError(f"(plot_time_series) `test` must be a `bool`. Got type: {type(test)}")
    
    # Information to output
    if verbose:
        print(f"(plot_time_series) `save_as`: {save_as}")

    # Check whether an existing figure and axis have been given
    if isinstance(fig, type(None)) or isinstance(axis, type(None)):
        if verbose:
            print(f"(plot_time_series) No pre-existing figure or axis given, creating new ones.")
        # Set up figure
        fig, axs = plt.subplots(1, 1, squeeze=False, figsize=[9, 6])
        # Select the only axis
        axis = axs[0,0]
    
    # Make title, if necessary
    if isinstance(plt_title, type(None)):
        plt_title = make_title(dataset, **kwargs)
    # Make label, if necessary
    if isinstance(y_ax_label, type(None)):
        y_ax_label = make_label(dataset, variable_id, verbose=verbose)

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
    time_series_axis = dataset.plot(
        ax = axis,
        xlim = xlims,
        ylim = ylims,
        color = line_clr,
        linestyle = line_style,
        **kwargs,
    )

    # Add a linear regression line if specified
    if add_regression:
        # Find the appropriate coordinate for the x-axis
        possible_coords = []
        for this_coord in dataset.coords:
            if dataset[this_coord].size > 1:
                possible_coords.append(this_coord)
        if len(possible_coords) == 1:
            x_var = possible_coords[0]
        else:
            raise ValueError(f"(plot_time_series) `dataset` must only have one coordinate with a size larger than 1.\nFound the following possible coordinates: {possible_coords}")
        if x_var == 'time':
            x_vals = np.array(get_epoch_times(
                dataset,
                x_var,
                verbose=verbose,
            ))
        else:
            x_vals = dataset[x_var].values
        # Take the regression 
        regressions = trend_in_time(
            dataset,
            time_dim = x_var,
            verbose = verbose,
        )
        reg_m = regressions[f'{variable_id}_trends'].values
        reg_b = regressions[f'{variable_id}_intercepts'].values
        print(f"(plot_time_series) Slope of `{variable_id}` regression line: {reg_m: .5e}")
        if verbose:
            print(f"(plot_time_series) Intercept of `{variable_id}` regression line: {reg_b: .5e}")
        if isinstance(reg_label, type(None)):
            # Format the label
            reg_label = f"{str(reg_m)[:6]}x+{str(reg_b)[:6]}"
        # Plot the regression line
        time_series_axis = axis.plot(
            dataset[x_var].values, 
            x_vals * reg_m + reg_b, 
            color = line_clr,
            linewidth = 3,
            label = reg_label,
        )
    # Modify the plot
    axis.set_title(plt_title)
    axis.set_ylabel(y_ax_label)
    axis.set_xlabel('')
    if include_legend:
        axis.legend()

    return time_series_axis
