import numpy as np
import xarray as xr

def find_standard_error(
    polyfit_residuals: xr.DataArray,
    n_dof: (int, float),
    verbose: bool = False,
    **kwargs,
):
    """ Sum a dataset by year along the time axis.

        Groups the dataset by year and sums each year.
        This results in one time step for each year in the given dataset.

        Parameters
        ----------
        polyfit_residuals : `int`, `float`, `xarray.DataArray`
            The array of sum of square residuals from the `polyfit_residuals` variable in the output of `xarray.polyfit` run with `full=True`. 
        n_dof : `int`, `float`
            The number of degrees of freedom to use.
        verbose : `bool`, optional
            Whether to verbosely output information as the function executes.
            Default is `False`.
        **kwargs
            Keyword arguments to handle extras that might have been passed by the function above this one.

        Returns
        -------
        standard_errors : `numpy.float64`, `xarray.DataArray`
            The standard error.
            If the data type of the given `polyfit_residuals` was `int` or `float`, the return type will be `numpy.float64`.
            If the data type of the given `polyfit_residuals` was `xarray.DataArray`, the return type will be `xarray.DataArray`.
        
        Examples
        --------
        >>> from arctichoke.analysis import find_standard_error
        >>> find_standard_error(175, 12)
        np.float64(4.183300132670378)
    """
    # Verify input arguments
    if not isinstance(polyfit_residuals, (int, float, xr.DataArray)):
        raise TypeError(f"(find_standard_error) `polyfit_residuals` must be a `xarray.DataArray`. Got type: {type(polyfit_residuals)}")
    if not isinstance(n_dof, (int, float)):
        raise TypeError(f"(find_standard_error) `n_dof` must be an integer or `float`. Got type: {type(n_dof)}")
    if not isinstance(verbose, bool):
        raise TypeError(f"(find_standard_error) `verbose` must be a `bool`. Got type: {type(verbose)}")
    
    # Calculate the standard error
    standard_errors = np.sqrt( polyfit_residuals / (n_dof - 2) )

    # If given a Data Array, change the name of the returned variable
    if isinstance(standard_errors, xr.DataArray):
        standard_errors.name = 'standard_errors'

    return standard_errors
