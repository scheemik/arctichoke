from datetime import datetime

def get_current_datetime_str(
    str_format: str = "%Y-%m-%dT%H:%M:%SZ",
):
    """ Get the current datetime in UTC.

        Format the current datetime into a string based on the given format string.

        Parameters
        ----------
        str_format : `str`, optional
            The format string by which to format the current datetime. 
            Default is `"%Y-%m-%dT%H:%M:%SZ"`.

        Returns
        -------
        datetime_str : `str`
            The formatted current datetime as a string.
        
        Examples
        --------
        >>> from seaicecp import get_current_datetime_str
        >>> get_current_datetime_str
    """
    # Verify input arguments
    if not isinstance(str_format, (str, type(None))):
        raise TypeError(f"(get_current_datetime_str) `str_format` must be a string. Got type: {type(str_format)}")
    
    # Get the current datetime
    current_datetime = datetime.now()

    # Format the datetime
    current_datetime = current_datetime.strftime(str_format)

    return current_datetime