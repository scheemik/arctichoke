import os
import warnings
warnings.filterwarnings("error")

from arctichoke import path

def test_list_variable_files():
    """Test the `list_variable_files` function."""
    # Define test cases that should not raise warnings
    ## Note: The expected output of these test cases is manually kept up to date
    test_cases = [
        {
            'source_id': 'AWI-CM-1-1-HR',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_list_len': 1,
        },
        {
            'source_id': 'AWI-CM-1-1-HR',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'control-1950',
            'variant_label': None,
            'expected_list_len': 1,
        },
        {
            'source_id': 'AWI-CM-1-1-LR',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_list_len': 1,
        },
        {
            'source_id': 'BCC-CSM2-HR',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_list_len': 1,
        },
        {
            'source_id': 'CESM1-CAM5-SE-HR',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_list_len': 1,
        },
        {
            'source_id': 'CESM1-CAM5-SE-LR',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'control-1950',
            'variant_label': None,
            'expected_list_len': 1,
        },
        {
            'source_id': 'EC-Earth3P',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'highres-future',
            'variant_label': None,
            'expected_list_len': 1,
        },
        {
            'source_id': 'EC-Earth3P-HR',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'highres-future',
            'variant_label': None,
            'expected_list_len': 1,
        },
        {
            'source_id': 'EC-Earth3P-HR',
            'variable_id': 'siage',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'hist-1950',
            'variant_label': 'r2i1p2f1',
            'expected_list_len': 65,
        },
        {
            'source_id': 'EC-Earth3P-HR',
            'variable_id': 'sispeed',
            'version_id': '*',
            'with_modification': 'trim_CAA_',
            'experiment_id': 'hist-1950',
            'variant_label': 'r1i1p2f1',
            'expected_list_len': 65,
        },
        {
            'source_id': 'EC-Earth3P-HR',
            'variable_id': 'sislow',
            'version_id': 'v20260617',
            'with_modification': 'trim_CAA_',
            'experiment_id': 'hist-1950',
            'variant_label': 'r1i1p2f1',
            'expected_list_len': 65,
        },
        {
            'source_id': 'EC-Earth3P-HR',
            'variable_id': 'siu',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'hist-1950',
            'variant_label': 'r3i1p2f1',
            'expected_list_len': 65,
        },
        {
            'source_id': 'HadGEM3-GC31-HH',
            'variable_id': 'siage',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_list_len': 65,
        },
        {
            'source_id': 'HadGEM3-GC31-HM',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_list_len': 1,
        },
        {
            'source_id': 'HadGEM3-GC31-HM',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'highres-future',
            'variant_label': None,
            'expected_list_len': 1,
        },
        {
            'source_id': 'HadGEM3-GC31-HM',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'control-1950',
            'variant_label': None,
            'expected_list_len': 1,
        },
        {
            'source_id': 'HadGEM3-GC31-LL',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_list_len': 1,
        },
        {
            'source_id': 'HadGEM3-GC31-LL',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'highres-future',
            'variant_label': None,
            'expected_list_len': 1,
        },
        {
            'source_id': 'HadGEM3-GC31-LL',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'control-1950',
            'variant_label': None,
            'expected_list_len': 1,
        },
        {
            'source_id': 'HadGEM3-GC31-LL',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'spinup-1950',
            'variant_label': None,
            'expected_list_len': 1,
        },
        {
            'source_id': 'HadGEM3-GC31-MM',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_list_len': 1,
        },
        {
            'source_id': 'HadGEM3-GC31-MM',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'highres-future',
            'variant_label': None,
            'expected_list_len': 1,
        },
        {
            'source_id': 'HadGEM3-GC31-MM',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'control-1950',
            'variant_label': None,
            'expected_list_len': 1,
        },
        {
            'source_id': 'HadGEM3-GC31-MM',
            'variable_id': 'areacello',
            'version_id': '*',
            'with_modification': None,
            'experiment_id': 'spinup-1950',
            'variant_label': None,
            'expected_list_len': 1,
        },
    ]
    for test_case in test_cases:
        actual = path.list_variable_files(
            source_id=test_case['source_id'], 
            variable_id=test_case['variable_id'],
            version_id=test_case['version_id'], 
            with_modification=test_case['with_modification'],
            experiment_id=test_case['experiment_id'],
            variant_label=test_case['variant_label'],
        )
        assert len(actual) == test_case['expected_list_len'], f"`list_variable_files` failed on test case: {test_case}."

    # Define test cases that should raise warnings
    ## Note: The expected output of these test cases is manually kept up to date
    test_cases = [
        {
            'source_id': 'EC-Earth3P-HR',
            'variable_id': 'siage',
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_list_len': 65,
        },
        {
            'source_id': 'EC-Earth3P-HR',
            'variable_id': 'siconc',
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_list_len': 65,
        },
    ]
    for test_case in test_cases:
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            # Trigger a warning.
            actual = path.list_variable_files(
                source_id=test_case['source_id'], 
                variable_id=test_case['variable_id'],
                experiment_id=test_case['experiment_id'],
                variant_label=test_case['variant_label'],
            )
            assert len(actual) == test_case['expected_list_len'], f"`list_variable_files` failed on test case: {test_case}."
            # Verify a warning was triggered
            assert len(w) == 1, f"`list_variable_files` did not trigger a warning on the test case {test_case}"
            # Verify the type of that warning
            assert issubclass(w[-1].category, UserWarning), f"`list_variable_files` did not trigger a `UserWarning` warning on the test case {test_case}. \nGot: {w[-1].category}"
            # Verify the warning message contains the expected text
            assert "More than one file path found" in str(w[-1].message), f"`list_variable_files` did not trigger a warning with the expected message on the test case {test_case}. \nGot: {w[-1].message}"

    # Define invalid test cases
    invalid_test_cases = [
        {
            'source_id': 'invalid_string',
            'variable_id': 'sithick',
            'experiment_id': 'hist-1950',
            'variant_label': 'r1i1p2f1',
        },
        {
            'source_id': 'EC-Earth3P-HR',
            'variable_id': 'invalid_string',
            'experiment_id': 'hist-1950',
            'variant_label': 'r1i1p2f1',
        },
        {
            'source_id': 'EC-Earth3P-HR',
            'variable_id': 'sithick',
            'experiment_id': 'invalid_string',
            'variant_label': 'r1i1p2f1',
        },
        {
            'source_id': 'EC-Earth3P-HR',
            'variable_id': 'sithick',
            'experiment_id': 'hist-1950',
            'variant_label': 'invalid_string',
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = path.list_variable_files(
                source_id = invalid_test_case['source_id'],
                variable_id = invalid_test_case['variable_id'],
                experiment_id = invalid_test_case['experiment_id'],
                variant_label = invalid_test_case['variant_label'],
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`list_variable_files` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`list_variable_files` did not raise an exception on invalid test case {invalid_test_case}"
    
    # Define a list of invalid strings
    invalid_strings = [
        1234,
        3.14,
        None,
        [],
        {}
    ]
    for invalid_string in invalid_strings:
        # Test with `source_id`
        try:
            actual = path.list_variable_files(
                source_id = invalid_string,
                variable_id = test_cases[0]['variable_id'],
            )
        except (TypeError) as e:
            assert True, f"`list_variable_files` raised an exception on invalid `source_id`: {e}"
        else:
            assert False, f"`list_variable_files` did not raise an exception on invalid `source_id` {invalid_string}"
        # Test with `variable_id`
        try:
            actual = path.list_variable_files(
                source_id = test_cases[0]['source_id'],
                variable_id = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`list_variable_files` raised an exception on invalid `variable_id`: {e}"
        else:
            assert False, f"`list_variable_files` did not raise an exception on invalid `variable_id` {invalid_string}"
        # Test with `version_id`
        try:
            actual = path.list_variable_files(
                source_id = test_cases[0]['source_id'],
                variable_id = test_cases[0]['variable_id'],
                version_id = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`list_variable_files` raised an exception on invalid `source_id`: {e}"
        else:
            assert False, f"`list_variable_files` did not raise an exception on invalid `source_id` {invalid_string}"
        # Test with `with_modification`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = path.list_variable_files(
                    source_id = test_cases[0]['source_id'],
                    variable_id = test_cases[0]['variable_id'],
                    with_modification = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`list_variable_files` raised an exception on invalid `with_modification`: {e}"
            else:
                assert False, f"`list_variable_files` did not raise an exception on invalid `with_modification` {invalid_string}"
        # Test with `experiment_id`
        try:
            actual = path.list_variable_files(
                source_id = test_cases[0]['source_id'],
                variable_id = test_cases[0]['variable_id'],
                experiment_id = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`list_variable_files` raised an exception on invalid `experiment_id`: {e}"
        else:
            assert False, f"`list_variable_files` did not raise an exception on invalid `experiment_id` {invalid_string}"
        # Test with `variant_label`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = path.list_variable_files(
                    source_id = test_cases[0]['source_id'],
                    variable_id = test_cases[0]['variable_id'],
                    variant_label = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`list_variable_files` raised an exception on invalid `variant_label`: {e}"
            else:
                assert False, f"`list_variable_files` did not raise an exception on invalid `variant_label` {invalid_string}"

def test_select_files_by_time():
    """Test the `select_files_by_time` function."""
    # Create a list of example file paths
    example_file_paths = [
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195101-195112.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195201-195212.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195301-195312.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195401-195412.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195501-195512.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195601-195612.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195701-195712.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195801-195812.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195901-195912.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_196001-196012.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_196101-196112.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_196201-196212.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_196301-196312.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_196401-196412.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_196501-196512.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_196601-196612.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_196701-196712.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_196801-196812.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_196901-196912.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_197001-197012.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_197101-197112.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_197201-197212.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_197301-197312.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_197401-197412.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_197501-197512.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_197601-197612.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_197701-197712.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_197801-197812.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_197901-197912.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_198001-198012.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_198101-198112.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_198201-198212.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_198301-198312.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_198401-198412.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_198501-198512.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_198601-198612.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_198701-198712.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_198801-198812.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_198901-198912.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_199001-199012.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_199101-199112.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_199201-199212.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_199301-199312.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_199401-199412.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_199501-199512.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_199601-199612.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_199701-199712.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_199801-199812.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_199901-199912.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_200001-200012.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_200101-200112.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_200201-200212.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_200301-200312.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_200401-200412.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_200501-200512.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_200601-200612.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_200701-200712.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_200801-200812.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_200901-200912.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201001-201012.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201101-201112.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201201-201212.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201301-201312.nc',
        '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_201401-201412.nc'
    ]
    # Define test cases that should not raise warnings
    ## Note: The expected output of these test cases is manually kept up to date
    test_cases = [
        {
            'data_filepaths': example_file_paths,
            'start': '1950-01-01',
            'end': '1960-01-01',
            'expected_files': [
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195101-195112.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195201-195212.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195301-195312.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195401-195412.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195501-195512.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195601-195612.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195701-195712.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195801-195812.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195901-195912.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_196001-196012.nc',
            ]
        },
        {
            'data_filepaths': example_file_paths,
            'start': 1950,
            'end': 1960,
            'expected_files': [
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195101-195112.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195201-195212.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195301-195312.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195401-195412.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195501-195512.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195601-195612.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195701-195712.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195801-195812.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195901-195912.nc',
                '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NWP_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_196001-196012.nc',
            ]
        },
    ]
    for test_case in test_cases:
        actual = path.select_files_by_time(
            data_filepaths=test_case['data_filepaths'], 
            start=test_case['start'],
            end=test_case['end'],
            test=True,
        )
        assert actual == test_case['expected_files'], f"`select_files_by_time` failed on test case: {test_case}."

    # Define invalid test cases
    invalid_test_cases = [
        {
            'data_filepaths': ['invalid_file_paths'],
            'start': 1950,
            'end': 1960,
        },
        {
            'data_filepaths': example_file_paths,
            'start': '1950',
            'end': 1960,
        },
        {
            'data_filepaths': example_file_paths,
            'start': 2000,
            'end': 1960,
        },
        {
            'data_filepaths': example_file_paths,
            'start': '2000-01-01',
            'end': '1960-01-01',
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = path.select_files_by_time(
                data_filepaths = invalid_test_case['data_filepaths'],
                start = invalid_test_case['start'],
                end = invalid_test_case['end'],
                test=True,
            )
        except (ValueError) as e:
            assert True, f"`select_files_by_time` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`select_files_by_time` did not raise an exception on invalid test case {invalid_test_case}"
    
    # Define a list of invalid strings
    invalid_strings = [
        1234,
        3.14,
        None,
        [],
        {}
    ]
    for invalid_string in invalid_strings:
        # Test with `data_filepaths`
        if not isinstance(invalid_string, type([])):
            try:
                actual = path.select_files_by_time(
                    data_filepaths = invalid_string,
                    start = 1950,
                    end = 1960,
                    test = True,
                )
            except (TypeError) as e:
                assert True, f"`select_files_by_time` raised an exception on invalid `data_filepaths`: {e}"
            else:
                assert False, f"`select_files_by_time` did not raise an exception on invalid `data_filepaths` {invalid_string}"
        # Test with `start`
        try:
            actual = path.select_files_by_time(
                data_filepaths = example_file_paths,
                start = invalid_string,
                end = 1960,
                test = True,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`select_files_by_time` raised an exception on invalid `start`: {e}"
        else:
            assert False, f"`select_files_by_time` did not raise an exception on invalid `start` {invalid_string}"
        # Test with `end`
        try:
            actual = path.select_files_by_time(
                data_filepaths = example_file_paths,
                start = 1950,
                end = invalid_string,
                test = True,
            )
        except (TypeError, ValueError) as e:
            assert True, f"`select_files_by_time` raised an exception on invalid `end`: {e}"
        else:
            assert False, f"`select_files_by_time` did not raise an exception on invalid `end` {invalid_string}"
        # Test with `test`
        try:
            actual = path.select_files_by_time(
                data_filepaths = example_file_paths,
                start = 1950,
                end = 1960,
                test = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`select_files_by_time` raised an exception on invalid `test`: {e}"
        else:
            assert False, f"`select_files_by_time` did not raise an exception on invalid `test` {invalid_string}"

