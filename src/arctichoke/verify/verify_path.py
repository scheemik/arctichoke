import os

def verify_path(
    path,
):
    """ Verify that the filepath exists.

        Check if the path to the data files exists and is valid.
        If not, raise an error.

        Parameters
        ----------
        path : `str`
            Relative path to the directory containing data files.

        Raises
        ------
        FileNotFoundError
            If the specified path does not exist.

        Returns
        -------
        path : `str`
            The verified path to the data files.

        Examples
        --------
        >>> verify_path('README.md')
        'README.md'
    """
    # Verify argument types
    if not isinstance(path, str):
        raise TypeError(f"(verify_path) `path` must be a string. Got type: {type(path)}")

    # Check whether the file path exists
    if not os.path.exists(path):
        # Try going up one directory, without adding the slash
        path0 = '..' + path
        if not os.path.exists(path0):
            # Try going up one directory, adding the slash
            path1 = '../' + path
            if not os.path.exists(path1):
                raise FileNotFoundError(f"(verify_path) The path {path} does not exist.")
            else:
                return path1
        else:
            return path0
    else:
        return path
