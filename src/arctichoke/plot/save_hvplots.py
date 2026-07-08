from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import holoviews as hv
from hvplot import save as hv_save

from arctichoke.verify import verify_path

def save_hvplot(
    hvplot_to_save,
    save_as: str,
):
    """ Save an `hvplot` to file.

        Save the given `hvplot` as either an `html` or `png` file in the `outputs/` directory.

        Parameters
        ----------
        hvplot_to_save : A type of `hvplot` object
            The  `hvplot` object to save to file.
        save_as : `str`
            The file path within the `outputs/` directory to which to save the plot.
            Must end in either `.html` or `.png`.

        Returns
        -------
        None
        
        Examples
        --------
        >>> 
    """
    # Verify input arguments
    if not isinstance(save_as, str):
        raise TypeError(f"(save_hvplot) `save_as` must be a string. Got type: {type(save_as)}")
    else:
        if not save_as.startswith('outputs/'):
            save_as = f"outputs/{save_as}"
    if '.html' in save_as:
        save_as_html = save_as
        save_as_png = None
    elif '.png' in save_as:
        save_as_html = save_as.replace('.png', '.html')
        save_as_png = save_as
    else:
        raise ValueError(f"(save_hvplot) `save_as` must be a string ending in either `.html` or `.png`. Got: {save_as}")
    
    print('(save_hvplot) save_as_html:', save_as_html)
    print('(save_hvplot) save_as_png:', save_as_png)
    
    # Save as an `html`, which is needed either way
    print(f"(save_hvplot) Saving to {save_as_html}")
    hv_save(hvplot_to_save, save_as_html)
    # Save as a `png`, if applicable
    if not isinstance(save_as_png, type(None)):
        html_to_png(save_as_html, save_as_png)

def html_to_png(
    html_filename: str, 
    png_filename: str = None,
):
    """ Save an `html` `hvplot` as a `png`.

        Load a previously-saved `html` format plot from `hvplot`, launch a headless browser in which to load it, take a screenshot, and save it to a `png` file.

        Parameters
        ----------
        html_filename : `str`
            The file path within the `outputs/` directory to the `html` file of the `hvplot`.
        png_filename : `str`, `None`, optional
            The file path within the `outputs/` directory to which to save the `png` image, or `None`. 

        Returns
        -------
        None
        
        Examples
        --------
        >>> 
    """
    # Verify input arguments
    if not isinstance(html_filename, str):
        raise TypeError(f"(html_to_png) `html_filename` must be a string. Got type: {type(html_filename)}")
    if not html_filename.startswith('outputs/'):
        html_filename = f"outputs/{html_filename}"
    html_filename = verify_path(html_filename)
    if '.html' not in html_filename:
        raise ValueError(f"(html_to_png) `html_filename` must be an `html` filepath. Got: {html_filename}")
    if not isinstance(png_filename, (str, type(None))):
        raise TypeError(f"(html_to_png) `png_filename` must be a string or `None`. Got type: {type(png_filename)}")
    if isinstance(png_filename, str):
        if '.png' not in png_filename:
            raise ValueError(f"(html_to_png) `png_filename` must be a `png` filepath. Got: {png_filename}")
    if isinstance(png_filename, type(None)):
        # Define the new path to be the same as `html_filename`, but with the `.png` extension
        png_filename = html_filename.replace('.html', '.png')

    print(f"(html_to_png) Saving {html_filename} to {png_filename}")

    # Activate the `bokeh` extension for HoloViews
    hv.extension("bokeh")

    # Set the options for the webdriver
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Start the chromium webdriver with the above options
    driver = webdriver.Chrome(options=options) 
    # Load the specified `html` plot
    driver.get("file://" + f"/workspace/{html_filename}")
    # Save a screenshot of that plot as a `png`
    driver.save_screenshot(png_filename)
    # Stop the webdriver
    driver.quit()