import xarray as xr

from arctichoke.dataset import grid_type
from arctichoke.dataset.example_dataset import make_example_dataset
from arctichoke.path import list_variable_files

def test_get_grid_type():
    """Test the `get_grid_type` function."""
    # Define test cases
    modified_example_dataset = make_example_dataset()
    modified_example_dataset = modified_example_dataset.isel(i=0)
    test_cases = [
        {
            'dataset': make_example_dataset(),
            'expected_grid_type': 'irregular',
        },
        {
            'dataset': modified_example_dataset,
            'expected_grid_type': 'other',
        },
        {
            'dataset': '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc',
            'expected_grid_type': 'irregular',
        },
        {
            'dataset': '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/Ofx/areacello/gn/v20190301/areacello_Ofx_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn.nc',
            'expected_grid_type': 'irregular',
        },
        {
            'dataset': '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/sithick/gn/v20170928/sithick_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_201401-201412.nc',
            'expected_grid_type': 'irregular',
        },
        {
            'dataset': '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/siconc/gn/v20170928/siconc_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_201401-201412.nc',
            'expected_grid_type': 'regular',
        },
        {
            'dataset': xr.open_dataset('/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/Ofx/areacello/gn/v20190301/areacello_Ofx_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn.nc'),
            'expected_grid_type': 'irregular',
        },
        {
            'dataset': xr.open_dataset('/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/sithick/gn/v20170928/sithick_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_201401-201412.nc'),
            'expected_grid_type': 'irregular',
        },
        {
            'dataset': xr.open_dataset('/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/siconc/gn/v20170928/siconc_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_201401-201412.nc'),
            'expected_grid_type': 'regular',
        },
    ]
    for test_case in test_cases:
        actual = grid_type.get_grid_type(
            dataset = test_case['dataset']
        )
        assert actual == test_case['expected_grid_type'], f"`get_grid_type` failed on test case: {test_case}.\nExpected: {test_case['expected_grid_type']}\nActual: {actual}"

    # Define invalid test cases
    invalid_example_dataset = make_example_dataset()
    invalid_example_dataset['test_var2'] = invalid_example_dataset['test_var']
    invalid_test_cases = [
        {
            'dataset': 'invalid_dataset',
        },
        {
            'dataset': 'invalid_dataset.nc',
        },
        {
            'dataset': invalid_example_dataset,
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = grid_type.get_grid_type(
                dataset = invalid_test_case['dataset'],
            )
        except (FileNotFoundError, TypeError, ValueError) as e:
            assert True, f"`get_grid_type` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`get_grid_type` did not raise an exception on invalid test case {invalid_test_case}"
    
    # Define a list of invalid datasets
    invalid_strings = [
        1234,
        3.14,
        None,
        [],
        {}
    ]
    for invalid_string in invalid_strings:
        # Test with `dataset`
        try:
            actual = grid_type.get_grid_type(
                dataset = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`get_grid_type` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`get_grid_type` did not raise an exception on invalid `dataset` {invalid_string}"

def test_summarize_grid_types():
    """Test the `summarize_grid_types` function."""
    # Define test cases
    test_cases = [
        {
            'datasets': [make_example_dataset()],
            'expected_grid_type_dict': {'total': 1, 'irregular': 1},
        },
        {
            'datasets': list_variable_files(
                source_id = 'EC-Earth3P-HR',
                variable_id = 'siconc',
                experiment_id = 'hist-1950',
                # experiment_id = 'highres-future',
                # variant_label = 'r1i1p1f1',
                variant_label = 'r1i1p2f1',
                # variant_label = 'r2i1p2f1',
                # variant_label = 'r3i1p2f1',
            ),
            'expected_grid_type_dict': {'total': 65, 'irregular': 65},
        },
        {
            'datasets': list_variable_files(
                source_id = 'EC-Earth3P-HR',
                variable_id = 'areacello',
                experiment_id = 'highres-future',
            ),
            'expected_grid_type_dict': {'total': 1, 'irregular': 1},
        },
        {
            'datasets': list_variable_files(
                source_id = 'EC-Earth3P-HR',
                variable_id = 'siconc',
                experiment_id = 'highres-future',
                variant_label = 'r1i1p2f1',
            ),
            'expected_grid_type_dict': {'total': 36, 'irregular': 36},
        },
        {
            'datasets': list_variable_files(
                source_id = 'EC-Earth3P-HR',
                variable_id = 'siconc',
                experiment_id = 'highres-future',
                variant_label = 'r3i1p2f1',
            ),
            'expected_grid_type_dict': {'total': 85, 'irregular': 85},
        },
        {
            'datasets': list_variable_files(
                source_id = 'HadGEM3-GC31-HH',
                variable_id = 'siconc',
                experiment_id = 'hist-1950',
            ),
            'expected_grid_type_dict': {'total': 64, 'irregular': 64},
        },
        {
            'datasets': list_variable_files(
                source_id = 'HadGEM3-GC31-HM',
                variable_id = 'sithick',
                experiment_id = 'hist-1950',
                variant_label = 'r1i2p1f1',
            ),
            'expected_grid_type_dict': {'total': 65, 'irregular': 65},
        },
        {
            'datasets': list_variable_files(
                source_id = 'HadGEM3-GC31-MM',
                variable_id = 'siconc',
                experiment_id = 'highres-future',
                variant_label = 'r1i1p1f1',
            ),
            'expected_grid_type_dict': {'total': 36, 'regular': 36},
        },
        {
            'datasets': list_variable_files(
                source_id = 'HadGEM3-GC31-MM',
                variable_id = 'siconc',
                experiment_id = 'highres-future',
                variant_label = 'r1i3p1f1',
            ),
            'expected_grid_type_dict': {'total': 36, 'regular': 36},
        },
        {
            'datasets': list_variable_files(
                source_id = 'HadGEM3-GC31-MM',
                variable_id = 'sithick',
                experiment_id = 'hist-1950',
                variant_label = 'r1i2p1f1',
            ),
            'expected_grid_type_dict': {'total': 65, 'irregular': 65},
        },
        {
            'datasets': list_variable_files(
                source_id = 'EC-Earth3P-HR',
                variable_id = 'siconc',
                experiment_id = 'hist-1950',
                variant_label = 'r1i1p2f1',
            ) + list_variable_files(
                source_id = 'HadGEM3-GC31-MM',
                variable_id = 'siconc',
                experiment_id = 'hist-1950',
                variant_label = 'r1i2p1f1',
            ),
            'expected_grid_type_dict': {'total': 130, 'irregular': 65, 'regular': 65},
        },
    ]
    for test_case in test_cases:
        actual = grid_type.summarize_grid_types(
            datasets = test_case['datasets']
        )
        assert actual == test_case['expected_grid_type_dict'], f"`summarize_grid_types` failed on test case: {test_case}.\nExpected: {test_case['expected_grid_type_dict']}\nActual: {actual}"
    
    # Define a list of invalid datasets
    invalid_strings = [
        1234,
        3.14,
        None,
        {}
    ]
    for invalid_string in invalid_strings:
        # Test with `datasets`
        try:
            actual = grid_type.summarize_grid_types(
                datasets = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`summarize_grid_types` raised an exception on invalid `datasets`: {e}"
        else:
            assert False, f"`summarize_grid_types` did not raise an exception on invalid `datasets` {invalid_string}"
