import xarray as xr

from seaicecp.plot import labels_and_titles
from seaicecp.dataset.example_dataset import make_example_dataset

def test_make_title():
    """Test the `make_title` function."""
    # Define test cases
    test_cases = [
        {
            'dataset': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc',
            'expected_title': 'EC-Earth3P-HR hist-1950 r1i1p2f1 ',
        },
        {
            'dataset': xr.open_dataset('/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc').isel(time=0),
            'expected_title': 'EC-Earth3P-HR hist-1950 r1i1p2f1 2014-01-16T12:00:00.000000000 ',
        },
        {
            'dataset': xr.open_dataset('/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r2i1p2f1/SImon/silandfast/gn/v20260617/trim_CAA_silandfast_SImon_EC-Earth3P-HR_hist-1950_r2i1p2f1_gn_195001-195012.nc').isel(time=1),
            'expected_title': 'EC-Earth3P-HR hist-1950 r2i1p2f1 1950-02-15T00:00:00.000000000 ',
        },
        {
            'dataset': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/Ofx/areacello/gn/v20190301/areacello_Ofx_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn.nc',
            'expected_title': 'HadGEM3-GC31-MM hist-1950 r1i1p1f1 ',
        },
        {
            'dataset': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/sithick/gn/v20170928/sithick_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_201401-201412.nc',
            'expected_title': 'HadGEM3-GC31-MM hist-1950 r1i1p1f1 ',
        },
        {
            'dataset': xr.open_dataset('/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/sithick/gn/v20170928/sithick_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_201401-201412.nc').isel(time=1),
            'expected_title': 'HadGEM3-GC31-MM hist-1950 r1i1p1f1 2014-02-16 00:00:00 ',
        },
    ]
    for test_case in test_cases:
        actual_title = labels_and_titles.make_title(
            dataset = test_case['dataset']
        )
        assert actual_title == test_case['expected_title'], f"`make_title` failed on test case: {test_case}.\nExpected title: {test_case['expected_title']}\nActual title: {actual_title}"

    # Define invalid test cases
    invalid_example_dataset = make_example_dataset()
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
            actual = labels_and_titles.make_title(
                dataset = invalid_test_case['dataset'],
            )
        except (FileNotFoundError, TypeError, ValueError, KeyError) as e:
            assert True, f"`make_title` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`make_title` did not raise an exception on invalid test case {invalid_test_case}"
    
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
            actual = labels_and_titles.make_title(
                dataset = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_title` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`make_title` did not raise an exception on invalid `dataset` {invalid_string}"
        # Test with `add_source_id`
        try:
            actual = labels_and_titles.make_title(
                dataset = test_cases[0]['dataset'],
                add_source_id = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_title` raised an exception on invalid `add_source_id`: {e}"
        else:
            assert False, f"`make_title` did not raise an exception on invalid `add_source_id` {invalid_string}"
        # Test with `add_experiment_id`
        try:
            actual = labels_and_titles.make_title(
                dataset = test_cases[0]['dataset'],
                add_experiment_id = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_title` raised an exception on invalid `add_experiment_id`: {e}"
        else:
            assert False, f"`make_title` did not raise an exception on invalid `add_experiment_id` {invalid_string}"
        # Test with `add_variant_label`
        try:
            actual = labels_and_titles.make_title(
                dataset = test_cases[0]['dataset'],
                add_variant_label = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_title` raised an exception on invalid `add_variant_label`: {e}"
        else:
            assert False, f"`make_title` did not raise an exception on invalid `add_variant_label` {invalid_string}"
        # Test with `add_time_stamp`
        try:
            actual = labels_and_titles.make_title(
                dataset = test_cases[0]['dataset'],
                add_time_stamp = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_title` raised an exception on invalid `add_time_stamp`: {e}"
        else:
            assert False, f"`make_title` did not raise an exception on invalid `add_time_stamp` {invalid_string}"

def test_make_label():
    """Test the `make_label` function."""
    # Define test cases
    test_cases = [
        {
            'dataset': make_example_dataset(test_var_name='test_var'),
            'var': 'test_var',
            'add_name': True,
            'add_units': True,
            'expected_label': 'test_var ',
        },
        {
            'dataset': make_example_dataset(test_var_name='test_var'),
            'var': 'test_var',
            'add_name': False,
            'add_units': False,
            'expected_label': '',
        },
        {
            'dataset': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc',
            'var': 'siconc',
            'add_name': True,
            'add_units': True,
            'expected_label': 'Sea Ice Area Fraction (Ocean Grid) (%) ',
        },
        {
            'dataset': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc',
            'var': 'siconc',
            'add_name': True,
            'add_units': False,
            'expected_label': 'Sea Ice Area Fraction (Ocean Grid) ',
        },
        {
            'dataset': xr.open_dataset('/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc')['siconc'],
            'var': None,
            'add_name': True,
            'add_units': True,
            'expected_label': 'Sea Ice Area Fraction (Ocean Grid) (%) ',
        },
        {
            'dataset': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r2i1p2f1/SImon/silandfast/gn/v20260617/trim_CAA_silandfast_SImon_EC-Earth3P-HR_hist-1950_r2i1p2f1_gn_195001-195012.nc',
            'var': 'silandfast',
            'add_name': True,
            'add_units': True,
            'expected_label': 'silandfast ',
        },
        {
            'dataset': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/Ofx/areacello/gn/v20190301/areacello_Ofx_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn.nc',
            'var': 'areacello',
            'add_name': True,
            'add_units': True,
            'expected_label': 'Grid-Cell Area for Ocean Variables (m2) ',
        },
        {
            'dataset': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/Ofx/areacello/gn/v20190301/areacello_Ofx_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn.nc',
            'var': 'areacello',
            'add_name': False,
            'add_units': True,
            'expected_label': '(m2) ',
        },
        {
            'dataset': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/sithick/gn/v20170928/sithick_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_201401-201412.nc',
            'var': 'sithick',
            'add_name': True,
            'add_units': True,
            'expected_label': 'Sea Ice Thickness (m) ',
        },
        {
            'dataset': xr.open_dataset('/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/sithick/gn/v20170928/sithick_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_201401-201412.nc')['sithick'],
            'var': None,
            'add_name': True,
            'add_units': True,
            'expected_label': 'Sea Ice Thickness (m) ',
        },
    ]
    for test_case in test_cases:
        actual_title = labels_and_titles.make_label(
            dataset = test_case['dataset'],
            var = test_case['var'],
            add_name = test_case['add_name'],
            add_units = test_case['add_units'],
        )
        assert actual_title == test_case['expected_label'], f"`make_label` failed on test case: {test_case}.\nExpected title: {test_case['expected_label']}\nActual title: {actual_title}"

    # Define invalid test cases
    invalid_test_cases = [
        {
            'dataset': 'invalid_dataset',
            'var': 'test_var',
        },
        {
            'dataset': 'invalid_dataset.nc',
            'var': 'test_var',
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = labels_and_titles.make_label(
                dataset = invalid_test_case['dataset'],
                var = invalid_test_case['var'],
            )
        except (FileNotFoundError, TypeError, ValueError, KeyError) as e:
            assert True, f"`make_label` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`make_label` did not raise an exception on invalid test case {invalid_test_case}"
    
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
            actual = labels_and_titles.make_label(
                dataset = invalid_string,
                var = 'siconc',
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_label` raised an exception on invalid `dataset`: {e}"
        else:
            assert False, f"`make_label` did not raise an exception on invalid `dataset` {invalid_string}"
        # Test with `var`
        try:
            actual = labels_and_titles.make_label(
                dataset = test_cases[0]['dataset'],
                var = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_label` raised an exception on invalid `var`: {e}"
        else:
            assert False, f"`make_label` did not raise an exception on invalid `var` {invalid_string}"
        # Test with `add_name`
        try:
            actual = labels_and_titles.make_label(
                dataset = test_cases[0]['dataset'],
                var = test_cases[0]['var'],
                add_name = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_label` raised an exception on invalid `add_name`: {e}"
        else:
            assert False, f"`make_label` did not raise an exception on invalid `add_name` {invalid_string}"
        # Test with `add_units`
        try:
            actual = labels_and_titles.make_label(
                dataset = test_cases[0]['dataset'],
                var = test_cases[0]['var'],
                add_units = invalid_string,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`make_label` raised an exception on invalid `add_units`: {e}"
        else:
            assert False, f"`make_label` did not raise an exception on invalid `add_units` {invalid_string}"
