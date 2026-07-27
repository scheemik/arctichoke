# Define parameters for the variables used in this project

sea_ice_vars = {
    'test_var': {
        'plot_range': None,
        'marker_var': False,
    },
    'siage': {
        'plot_range': [0, 5],
        'marker_var': False,
    },
    'siage2': {
        'plot_range': [0, 10],
        'marker_var': False,
    },
    'siconc': {
        'plot_range': [0, 100],
        'marker_var': False,
    },
    'siconc2': {
        'plot_range': [0, 100],
        'marker_var': False,
    },
    'sispeed': {
        'plot_range': None,
        'marker_var': False,
    },
    'sithick': {
        'plot_range': [0, 10],
        'marker_var': False,
    },
    'siu': {
        'plot_range': None,
        'marker_var': False,
    },
    'siv': {
        'plot_range': None,
        'marker_var': False,
    },
    'sivol': {
        'plot_range': [0, 10],
        'marker_var': False,
    },
    # Marker variables
    'silandfast': {
        'plot_range': None,
        'marker_var': True,
        'label_name': 'Landfast Ice',
    },
    'simultiyear': {
        'plot_range': None,
        'marker_var': True,
        'label_name': 'Multi-Year Ice',
    },
    'sipacked': {
        'plot_range': None,
        'marker_var': True,
        'label_name': 'Packed Ice',
    },
    'sislow': {
        'plot_range': None,
        'marker_var': True,
        'label_name': 'Slow Ice',
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