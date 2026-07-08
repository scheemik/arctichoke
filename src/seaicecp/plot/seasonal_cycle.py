from datetime import datetime
import matplotlib
import matplotlib.cm as mplcm 
import matplotlib.colors as mplclrs
from matplotlib.figure import figaspect
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from arctichoke.dataset.field_mean import get_field_mean 
from arctichoke.path.file_lists import list_variable_files, select_files_by_time
import arctichoke.params as sps
from arctichoke.verify import verify_path

def plot_seasonal_cycle(
    datasets: [(str, xr.DataArray, xr.Dataset)],
    variable_id: str = None,
    take_mean: bool = False,
    ax: matplotlib.axes.Axes = None,
    plt_title: str = None,
    line_labels: [str] = None,
    line_styles: [str] = '-',
    xlims: [str, str] = None,
    ylims: [float, float] = None,
    c_map: [mplclrs.ListedColormap] = mplcm.viridis_r,
    c_map_label: str = 'Year',
    save_as: str = None,
    test: bool = False,
    **kwargs,
):
    """ Plot a seasonal cycle of the dataset.

        Plots a seasonal cycle of the given dataset for the given variable, if applicable.

        Parameters
        ----------
        datasets : list of `str`, `xarray.DataArray`, `xarray.Dataset`
            A list of datasets for which to make a plot.
        variable_id : `str`
            The name of the variable ID to plot.
        take_mean : `bool`, optional
            Whether to take the mean for each month across all the years.
            Default is `False`.
        ax : `matplotlib.axes.Axes`, optional
            The axes on which to plot the data.
            If `None`, a new figure is created.
            Default is `None`.
        plt_title : `str`, `None`, optional
            The title to use for the plot.
            Default is `None`, which uses a default title for the plot.
        line_labels : list of `str`, `None`, optional
            The labels to use for the lines that are plotted if `take_mean = True`.
            Default is `None`.
        line_styles : list of `str`, `None`, optional
            The line styles to use for the lines that are plotted if `take_mean = True`.
            Default is `'-'`.
        xlims : List of `float`, optional
            The limits to use for the x-axis on the plot in the following format:
                - [x_min, x_max]

            where `x_min` and `x_max` are strings in the format `YYYY-MM-DD`
            Default is `None`, which expands the x-axis to include all the data.
        ylims : List of `float`, optional
            The limits to use for the y-axis on the plot in the following format:
                - [y_min, y_max]
                
            Default is `None`, which expands the y-axis to include all the data.
        c_map : `matplotlib.colors.ListedColormap`, optional
            The color map to use for the different lines so their order is clearer.
            Default is `matplotlib.cm.viridis_r`, the reverse of `viridis`.
        c_map_label : `str`, `None`, optional
            The label to use on the colorbar.
            If `None`, then the colorbar will have no label.
            Default is `Year`.
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
            fig
            ax
        If `test` == `True` : 
            dataset : `xarray.DataArray`
        
        Examples
        --------
        >>> from arctichoke.dataset.field_mean import get_field_mean 
        >>> fldmean_xr = get_field_mean('example_siconc_dataset.nc')
        >>> from arctichoke.plot.seasonal_cycle import plot_seasonal_cycle
        >>> plot_seasonal_cycle(dataset = fldmean_xr, variable_id = 'siconc')
    """
    # Verify input arguments
    if not isinstance(datasets, type([])):
        if isinstance(datasets, (str, xr.Dataset, xr.DataArray)):
            datasets = [datasets]
    for dataset in datasets:
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
        for dataset in datasets:
            if isinstance(dataset, xr.Dataset):
                raise ValueError(f"(plot_seasonal_cycle) `variable_id` must be a string if `dataset` is `xr.Dataset`. Got type: {type(variable_id)}")
            else:
                variable_id = dataset.name
    if not isinstance(take_mean, bool):
        raise TypeError(f"(plot_seasonal_cycle) `take_mean` must be a `bool`. Got type: {type(take_mean)}")
    if not isinstance(ax, (matplotlib.axes.Axes, type(None))):
        raise TypeError(f"(plot_seasonal_cycle) `ax` must be a matplotlib Axes object or `None`. Got type: {type(ax)}")
    if isinstance(plt_title, type(None)):
        plt_title = f"Seasonal cycle of '{variable_id}'"
    elif not isinstance(plt_title, str):
        raise TypeError(f"(plot_seasonal_cycle) `plt_title` must be a string or `None`. Got type: {type(plt_title)}")
    if isinstance(line_labels, type([])):
        if not len(line_labels) == len(datasets):
            raise ValueError(f"(plot_seasonal_cycle) `line_labels` is a different length ({len(line_labels)}) than `datasets` ({len(datasets)}).")
        for line_label in line_labels:
            if not isinstance(line_label, str):
                raise TypeError(f"(plot_seasonal_cycle) `line_labels` must be a list of strings or `None`. Got type: {type(line_label)}")
    elif isinstance(line_labels, str):
        line_labels = [line_labels]*len(datasets)
    elif not isinstance(line_labels, type(None)):
        raise TypeError(f"(plot_seasonal_cycle) `line_labels` must be a list of strings or `None`. Got type: {type(line_labels)}")
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

    # Check whether to make a new figure or not
    if isinstance(ax, type(None)):
        # Create the figure
        fig = plt.figure()
        ax = fig.subplots(nrows=1, ncols=1)

    # Get limits for the y-axis
    if isinstance(ylims, type(None)):
        # Check whether the given variable is in the sea ice variable dictionary
        if variable_id in sps.sea_ice_vars.keys():
            # Check whether that variable has a plot range defined
            if 'plot_range' in sps.sea_ice_vars[variable_id].keys():
                ylims = sps.sea_ice_vars[variable_id]['plot_range']

    # Loop across the datasets
    for i in range(len(datasets)):
        dataset = datasets[i]
        if isinstance(line_labels, type([])):
            line_label = line_labels[i]
        else:
            line_label = line_labels
        if isinstance(line_styles, type([])):
            line_style = line_styles[i]
        else:
            line_style = line_styles
        # Get the data array to plot
        if isinstance(dataset, str):
            dataset = xr.open_dataset(dataset)
        if isinstance(dataset, xr.Dataset):
            dataset = dataset[variable_id]
    
        # Assemble the axis label
        var_long_name = dataset.attrs['long_name']
        var_units = dataset.attrs['units']
        var_axis_label = f"{var_long_name} ({var_units})"
        
        # Convert the data array into a data frame
        ## Using `.isel` to select the first index of the `lat` and `lon` coordinates
        ## so that these are dropped. It is assumed that the dataset coming in to this function
        ## is a field mean, so there should only be one `lat` and one `lon` value
        data_frame = dataset.isel(lat=0, lon=0).reset_coords(drop=True).to_dataframe()
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
            # Taking the mean results in a data series
            data_frame = data_frame.mean(axis=1)
            # Add the specified label as the name of the resulting data series
            data_frame.name = line_label
            # Modify the plot title
            if not plt_title.startswith('Mean'):
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
            ax = ax,
            xlim = xlims,
            ylim = ylims,
            ylabel = var_axis_label,
            title = plt_title,
            linestyle = line_style,
            legend = True,
            **kwargs,
        )
    # If there are more than 10 lines, remove the legend and replace with a colorbar
    if len(year_values) > 10:
        this_ax.get_legend().remove()
        plt.colorbar(
            cmapper, 
            ax = this_ax,
            label = c_map_label,
        )

    return ax

def multi_seasonal_cycle(
    source_id: str = 'EC-Earth3P-HR',
    variable_ids: [str] = ['siconc', 'sithick'],
    experiment_ids: [str] = ['hist-1950'],
    time_bounds_lists: dict = {
        'hist-1950': [
            [1950, 1959], 
            [2005, 2014],
        ],
        'highres-future': [
            [2015, 2024], 
            [2041, 2050]
        ],
    },
    variant_labels = [
        'r1i1p2f1', 
        'r2i1p2f1', 
        'r3i1p2f1',
    ],
    super_title: str = None,
    fig_scale: (int, float) = 2,
    save_as: str = None,
    test: bool = False,
    **kwargs,
):
    """ Plot multiple seasonal cycles of different datasets.

        Plots a seasonal cycle for each combination of parameters.
        Different experiments get their own axes, as well as different variables.
        Multiple time bounds and variant labels are plotted on the same axes.

        Parameters
        ----------
        source_id : `str`
            The name of the `source_id` to specify the model to plot.
        variable_ids : list of `str`
            The variable ID(s) to plot.
        experiment_ids : list of `str`, optional
            The experiment(s) to plot. 
            Default is `['hist-1950']`.
        time_bounds_lists : `dict`, optional
            A dictionary of the time bounds within which to plot.
            Each key in the dictionary is the name of an experiment and each value is a list of pairs of years.
            These time bounds will be passed to `select_files_by_time()`.
            Default is shown above.
        variant_labels : list of `str`, optional
            The variant label(s) to plot for each subplot.
            Default is shown above.
        super_title : `str`, `None`, optional
            The title for the overall figure.
            Default is `None`.
        fig_scale : `int`, `float`, optional
            The scale factor by which to resize the figure.
            Default is `2`. 
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
        `None`
        
        Examples
        --------
        >>> from arctichoke.plot.seasonal_cycle import multi_seasonal_cycle 
        >>> multi_seasonal_cycle(
                source_id = 'EC-Earth3P-HR',
                variable_ids = ['siconc'],
                super_title = 'Seasonal Cycles',
            )
    """
    # Verify input arguments
    if not isinstance(source_id, str):
        raise TypeError(f"(multi_seasonal_cycle) `source_id` must be a string. Got type: {type(source_id)}")
    if not isinstance(variable_ids, type([])):
        if isinstance(variable_ids, str):
            variable_ids = [variable_ids]
    for variable_id in variable_ids:
        if not isinstance(variable_id, str):
            raise TypeError(f"(multi_seasonal_cycle) `variable_id` must be a string. Got type: {type(variable_id)}")
    if not isinstance(time_bounds_lists, type({})):
        raise TypeError(f"(multi_seasonal_cycle) `time_bounds_lists` must be a dictionary. Got type: {type(time_bounds_lists)}")
    if not isinstance(experiment_ids, type([])):
        if isinstance(experiment_ids, str):
            experiment_ids = [experiment_ids]
    for experiment_id in experiment_ids:
        if not isinstance(experiment_id, str):
            raise TypeError(f"(multi_seasonal_cycle) `experiment_id` must be a string. Got type: {type(experiment_id)}")
        if not experiment_id in time_bounds_lists.keys():
            raise ValueError(f"(multi_seasonal_cycle) `experiment_id` must be in the `time_bound_lists.keys()`. Got: {experiment_id}\n\tAvailable keys: {time_bounds_lists.keys()}")
    for time_bounds in time_bounds_lists.values():
        for these_time_bounds in time_bounds:
            if not len(these_time_bounds) == 2:
                raise ValueError(f"(multi_seasonal_cycle) `time_bounds_lists` must contain lists of length 2. Got: {these_time_bounds}")
    if not isinstance(variant_labels, type([])):
        if isinstance(variant_labels, str):
            variant_labels = [variant_labels]
    for variant_label in variant_labels:
        if not isinstance(variant_label, str):
            raise TypeError(f"(multi_seasonal_cycle) `variant_label` must be a string. Got type: {type(variant_label)}")
    if not isinstance(super_title, str):
        raise TypeError(f"(multi_seasonal_cycle) `super_title` must be a string. Got type: {type(super_title)}")
    if not isinstance(save_as, (str, type(None))):
        raise TypeError(f"(plot_seasonal_cycle) `save_as` must be a string or `None`. Got type: {type(save_as)}")
    elif isinstance(save_as, str) and not '.png' in save_as:
        raise TypeError(f"(plot_seasonal_cycle) `save_as` must be a `.png` filepath. Got: {save_as}")
    if not isinstance(test, (type(True))):
        raise TypeError(f"(plot_seasonal_cycle) `test` must be a `bool`. Got type: {type(test)}")
    
    # Set up the figure
    n_rows = len(variable_ids)
    n_cols = len(experiment_ids)
    w, h = figaspect(n_rows/n_cols)
    fig_scale = 2
    this_fig = plt.figure(figsize=(w*fig_scale,h*fig_scale))
    # Use `squeeze=False` to ensure `this_ax` always has 2 dimensions
    this_ax = this_fig.subplots(nrows=n_rows, ncols=n_cols, squeeze=False)

    # Set up the line labels and styles
    time_bounds_len = len(time_bounds_lists[experiment_ids[0]][0])
    these_line_labels = variant_labels*time_bounds_len
    if time_bounds_len == 1:
        these_line_styles = ['-']*len(variant_labels)
    elif time_bounds_len == 2:
        these_line_styles = ['--']*len(variant_labels) + ['-']*len(variant_labels)
    else:
        raise TypeError(f"(plot_seasonal_cycle) Support for `time_bounds_lists` entries with lists longer than 2 has not yet been implemented. Got: {time_bounds_lists}")

    # Loop across rows for the different variables
    for j in range(len(variable_ids)):
        # Select the variable from the list
        this_variable = variable_ids[j]
        # Loop across columns for the experiments
        for i in range(len(experiment_ids)):
            this_experiment = experiment_ids[i]
            list_of_time_bounds = time_bounds_lists[this_experiment]
            these_datasets = []
            for these_time_bounds in list_of_time_bounds:
                for this_variant_label in variant_labels:
                    these_files = list_variable_files(
                        source_id = source_id,
                        variable_id = this_variable,
                        experiment_id = this_experiment,
                        variant_label = this_variant_label,
                        with_modification = 'trim_NWP_',
                    )

                    just_these_files = select_files_by_time(
                        data_filepaths = these_files,
                        start = min(these_time_bounds),
                        end = max(these_time_bounds),
                    )
                    print(just_these_files)

                    fldmean_xr = get_field_mean(
                        dataset = just_these_files,
                        save_as = None
                    )

                    these_datasets.append(fldmean_xr)

            this_ax[j,i] = plot_seasonal_cycle(
                datasets = these_datasets, 
                variable_id = this_variable,
                take_mean = True,
                ax = this_ax[j,i],
                plt_title = f"{source_id} ({this_experiment}) NWP Region",
                line_labels = these_line_labels,
                line_styles = these_line_styles,
            )
    plt.suptitle(super_title)