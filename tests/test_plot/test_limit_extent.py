import cartopy.crs as crs
import numpy as np
import xarray as xr

from arctichoke.dataset import  bound_lat, bound_lon
from arctichoke.plot import limit_extent
import arctichoke.params as sps

def test_get_limited_extent():
    """Test the `get_limited_extent` function."""
    # Define test cases
    test_cases = [
        {
            'map_projection': 'Orthographic',
            'map_bbox': [10, -10, 10, -10],
            'n_samples': 5,
            'padding': 0.,
            'lon_type': None,
            'expected_extent': (
                np.float64(-1107551.8669600263),
                np.float64(1107551.8669600263),
                np.float64(-1107551.8669600263),
                np.float64(1107551.8669600263)
            ),
        },
        {
            'map_projection': 'Orthographic',
            'map_bbox': [10, -10, 10, -10],
            'n_samples': 100,
            'padding': 0.,
            'lon_type': None,
            'expected_extent': (
                np.float64(-1107550.1458116504),
                np.float64(1107550.1458116504),
                np.float64(-1107551.8669600263),
                np.float64(1107551.8669600263)
            ),
        },
        {
            'map_projection': 'Orthographic',
            'map_bbox': [10, -10, 10, -10],
            'n_samples': 5,
            'padding': 0.1,
            'lon_type': None,
            'expected_extent': (
                np.float64(-1217005.9133439737),
                np.float64(1217005.9133439737),
                np.float64(-1217005.9133439737),
                np.float64(1217005.9133439737)
            ),
        },
        {
            'map_projection': 'Orthographic',
            'map_bbox': [90, -10, 10, -10],
            'n_samples': 5,
            'padding': 0.,
            'lon_type': None,
            'expected_extent': (
                np.float64(-1090725.6654453792),
                np.float64(1090725.6654453792),
                np.float64(-4885936.4063015515),
                np.float64(4885936.406301549)
            ),
        },
        {
            'map_projection': 'Orthographic',
            'map_bbox': [100, -10, 10, -10],
            'n_samples': 5,
            'padding': 0.,
            'lon_type': None,
            'expected_extent': (
                np.float64(-1090725.6654453792),
                np.float64(1090725.6654453792),
                np.float64(-4885936.4063015515),
                np.float64(4885936.406301549)
            ),
        },
        {
            'map_projection': 'Orthographic',
            'map_bbox': sps.CAA_BBOX,
            'n_samples': 100,
            'padding': 0.0,
            'lon_type': None,
            'expected_extent': (
                np.float64(-3122618.275802004),
                np.float64(2283425.766040278),
                np.float64(-1864748.419905291),
                np.float64(1650783.3278730563)
            ),
        },
        {
            'map_projection': 'Orthographic',
            'map_bbox': sps.CAA_BBOX,
            'n_samples': 100,
            'padding': 0.1,
            'lon_type': None,
            'expected_extent': (
                np.float64(-3375380.0714404564),
                np.float64(2623009.2640127367),
                np.float64(-2034308.475405136),
                np.float64(1650783.3278730563)
            ),
        },
    ]
    for test_case in test_cases:
        # Make sure the the coordinates aren't outside valid ranges
        test_case['map_bbox'][0] = bound_lat(test_case['map_bbox'][0])
        test_case['map_bbox'][1] = bound_lat(test_case['map_bbox'][1])
        test_case['map_bbox'][2] = bound_lon(test_case['map_bbox'][2], lon_type=test_case['lon_type'])
        test_case['map_bbox'][3] = bound_lon(test_case['map_bbox'][3], lon_type=test_case['lon_type'])
        # Calculate the central latitude and longitude based on the bounding box
        lat_cent = (test_case['map_bbox'][0]-test_case['map_bbox'][1])/2 + test_case['map_bbox'][1]
        lon_cent = (test_case['map_bbox'][2]-test_case['map_bbox'][3])/2 + test_case['map_bbox'][3]
        print(f'(test_get_limited_extent) lat_cent: {lat_cent}, lon_cent: {lon_cent}')
        # Create the projection
        if test_case['map_projection'] == 'Orthographic':
            this_map_proj = crs.Orthographic(central_latitude = lat_cent, central_longitude = lon_cent)
        elif test_case['map_projection'] == 'NorthPolarStereo':
            this_map_proj = crs.NorthPolarStereo(central_longitude = lon_cent)
        actual_extent = limit_extent.get_limited_extent(
            map_projection = this_map_proj,
            map_bbox = test_case['map_bbox'],
            n_samples = test_case['n_samples'],
            padding = test_case['padding'],
            lon_type = test_case['lon_type'],
            verbose = True,
        )
        assert actual_extent == test_case['expected_extent'], f"`get_limited_extent` failed on test case: {test_case}.\nExpected extent: {test_case['expected_extent']}\nActual extent: {actual_extent}"
    
    # Define a list of invalid strings
    invalid_strings = [
        1234,
        3.14,
        None,
        [],
        {}
    ]
    for invalid_string in invalid_strings:
        # Test with `map_projection`
        try:
            actual = limit_extent.get_limited_extent(
                map_projection = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`get_limited_extent` raised an exception on invalid `map_projection`: {e}"
        else:
            assert False, f"`get_limited_extent` did not raise an exception on invalid `map_projection` {invalid_string}"
        # Test with `map_bbox`
        try:
            actual = limit_extent.get_limited_extent(
                map_projection = this_map_proj,
                map_bbox = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`get_limited_extent` raised an exception on invalid `map_bbox`: {e}"
        else:
            assert False, f"`get_limited_extent` did not raise an exception on invalid `map_bbox` {invalid_string}"
        # Test with `verbose`
        try:
            actual = limit_extent.get_limited_extent(
                map_projection = this_map_proj,
                verbose = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`get_limited_extent` raised an exception on invalid `verbose`: {e}"
        else:
            assert False, f"`get_limited_extent` did not raise an exception on invalid `verbose` {invalid_string}"

    # Define a list of invalid numbers
    invalid_numbers = [
        '0',
        '0.5',
        '1234',
        1234,
        3.14,
        None,
        [],
        {}
    ]
    for invalid_number in invalid_numbers:
        # Test with `n_samples`
        if not isinstance(invalid_number, int):
            try:
                actual = limit_extent.get_limited_extent(
                    map_projection = this_map_proj,
                    n_samples = invalid_number,
                )
            except (TypeError, ValueError) as e:
                assert True, f"`get_limited_extent` raised an exception on invalid `n_samples`: {e}"
            else:
                assert False, f"`get_limited_extent` did not raise an exception on invalid `n_samples` {invalid_number}"
        # Test with `padding`
        try:
            actual = limit_extent.get_limited_extent(
                map_projection = this_map_proj,
                padding = invalid_number,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`get_limited_extent` raised an exception on invalid `padding`: {e}"
        else:
            assert False, f"`get_limited_extent` did not raise an exception on invalid `padding` {invalid_number}"
