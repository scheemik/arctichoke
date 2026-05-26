# Define parameters for the variables used in this project

sea_ice_vars = {
    'test_var': {
        'plot_range': None,
    },
    'siage': {
        'plot_range': None,
    },
    'siconc': {
        'plot_range': [0, 100],
    },
    'sithick': {
        'plot_range': None,
    },
    'siu': {
        'plot_range': None,
    },
    'siv': {
        'plot_range': None,
    },
}

# Meta variables used to structure the data
# These will appear in the lists of `data_vars`, but are not the actual variable of the file
meta_vars = [
    'time_bnds', 
    'vertices_latitude', 
    'vertices_longitude', 
    'latitude_bnds', 
    'longitude_bnds',
    'lat_bnds',
    'lon_bnds',
]