import warnings
warnings.filterwarnings("error")

from seaicecp import path

def test_list_available_variables():
    """Test the `list_available_variables` function."""
    # Define test cases
    ## Note: The expected output of these test cases is manually kept up to date and does not necessarily contain all models
    test_cases = [
        {
            'source_id': 'AWI-CM-1-1-HR',
            'experiment_id': None,
            'list_var_mods': False,
            'expected_var_dict': {
                'AWI/AWI-CM-1-1-HR': {
                    'control-1950': {'r1i1p1f2': ['areacello']},
                    'hist-1950': {'r1i1p1f2': ['areacello']},
                    'spinup-1950': {'r1i1p1f2': ['areacello']},
                },
            },
        },
        {
            'source_id': 'AWI-CM-1-1-HR',
            'experiment_id': None,
            'list_var_mods': True,
            'expected_var_dict': {
                'AWI/AWI-CM-1-1-HR': {
                    'control-1950': {'r1i1p1f2': {'Ofx': {'areacello': {'': 1}}}},
                    'hist-1950': {'r1i1p1f2': {'Ofx': {'areacello': {'': 1}}}},
                    'spinup-1950': {'r1i1p1f2': {'Ofx': {'areacello': {'': 1}}}},
                },
            },
        },
        {
            'source_id': 'BCC-CSM2-HR',
            'experiment_id': None,
            'list_var_mods': False,
            'expected_var_dict': {
                'BCC/BCC-CSM2-HR': {
                    'hist-1950': {'r1i1p1f1': ['areacello']},
                },
            },
        },
        {
            'source_id': 'CESM1-CAM5-SE-HR',
            'experiment_id': None,
            'list_var_mods': False,
            'expected_var_dict': {
                'NCAR/CESM1-CAM5-SE-HR': {
                    'highres-future': {'r1i1p1f1': ['areacello']},
                    'hist-1950': {'r1i1p1f1': ['areacello']},
                },
            },
        },
        {
            'source_id': 'EC-Earth3P-HR',
            'experiment_id': None,
            'list_var_mods': False,
            'expected_var_dict': {
                'EC-Earth-Consortium/EC-Earth3P-HR': {
                    'highres-future': {
                        'r1i1p2f1': ['sithick', 'siage', 'siv', 'siu', 'siconc'],
                        'r2i1p2f1': ['areacello', 'siv', 'sithick', 'siu', 'siage', 'siconc'],
                        'r3i1p2f1': ['siconc', 'siage', 'siu', 'sithick', 'siv']
                    },
                    'hist-1950': {
                        'r1i1p2f1': ['siu', 'siv', 'sithick', 'siage', 'siconc'],
                        'r2i1p2f1': ['siage', 'sithick', 'siv', 'siu', 'siconc'],
                        'r3i1p2f1': ['sithick', 'siage', 'siu', 'siv', 'siconc']
                    },
                },
            },
        },
        {
            'source_id': 'HadGEM3-GC31-HM',
            'experiment_id': None,
            'list_var_mods': False,
            'expected_var_dict': {
                'MOHC/HadGEM3-GC31-HM': {
                    'control-1950': {
                        'r1i1p1f1': ['areacello']
                    },
                    'highres-future': {
                        'r1i1p1f1': ['areacello', 'siu', 'siv', 'sithick', 'siconc', 'siage'],
                        'r1i3p1f1': ['siconc', 'siage', 'siv', 'sithick', 'siu']
                    },
                    'hist-1950': {
                        'r1i1p1f1': ['areacello', 'siage', 'siv', 'siu', 'siconc', 'sithick'],
                        'r1i3p1f1': ['siconc', 'sithick', 'siu', 'siage', 'siv']
                    },
                },
                'NERC/HadGEM3-GC31-HM': {
                    'highres-future': {
                        'r1i2p1f1': ['siv', 'siu', 'siconc', 'sithick', 'siage']
                    },
                    'hist-1950': {
                        'r1i2p1f1': ['siconc', 'siu', 'sithick', 'siv', 'siage']
                    },
                },
            },
        },
    ]
    for test_case in test_cases:
        actual = path.list_available_variables(
            source_id=test_case['source_id'], 
            experiment_id=test_case['experiment_id'],
            list_var_mods=test_case['list_var_mods'], 
        )
        assert actual == test_case['expected_var_dict'], f"`list_available_variables` failed on test case: {test_case}. \nActual: {actual}\nExpected: {test_case['expected_var_dict']}\nHas the expected list in `tests/test_path/test_find_data.py` been updated?"

    # Define invalid test cases
    invalid_test_cases = [
        {
            'source_id': 'invalid_string',
            'experiment_id': 'hist-1950',
            'data_dir': '/seaicecp_data/bergybits/data',
            'project': 'CMIP6',
            'activity_id': 'HighResMIP',
        },
        {
            'source_id': 'EC-Earth3P-HR',
            'experiment_id': 'invalid_string',
            'data_dir': '/seaicecp_data/bergybits/data',
            'project': 'CMIP6',
            'activity_id': 'HighResMIP',
        },
        {
            'source_id': 'EC-Earth3P-HR',
            'experiment_id': None,
            'data_dir': 'invalid_string',
            'project': 'CMIP6',
            'activity_id': 'HighResMIP',
        },
        {
            'source_id': 'EC-Earth3P-HR',
            'experiment_id': 'hist-1950',
            'data_dir': '/seaicecp_data/bergybits/data',
            'project': 'invalid_string',
            'activity_id': 'HighResMIP',
        },
        {
            'source_id': 'EC-Earth3P-HR',
            'experiment_id': 'hist-1950',
            'data_dir': '/seaicecp_data/bergybits/data',
            'project': 'CMIP6',
            'activity_id': 'invalid_string',
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = path.list_available_variables(
                source_id = invalid_test_case['source_id'],
                experiment_id = invalid_test_case['experiment_id'],
                data_dir = invalid_test_case['data_dir'],
                project = invalid_test_case['project'],
                activity_id = invalid_test_case['activity_id'],
            )
        except (FileNotFoundError) as e:
            assert True, f"`list_available_variables` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`list_available_variables` did not raise an exception on invalid test case {invalid_test_case}"
    
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
            actual = path.list_available_variables(
                source_id = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`list_available_variables` raised an exception on invalid `source_id`: {e}"
        else:
            assert False, f"`list_available_variables` did not raise an exception on invalid `source_id` {invalid_string}"
        # Test with `experiment_id`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = path.list_available_variables(
                    source_id = 'EC-Earth3P-HR',
                    experiment_id = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`list_available_variables` raised an exception on invalid `experiment_id`: {e}"
            else:
                assert False, f"`list_available_variables` did not raise an exception on invalid `experiment_id` {invalid_string}"
        # Test with `list_var_mods`
        try:
            actual = path.list_available_variables(
                source_id = 'EC-Earth3P-HR',
                list_var_mods = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`list_available_variables` raised an exception on invalid `list_var_mods`: {e}"
        else:
            assert False, f"`list_available_variables` did not raise an exception on invalid `list_var_mods` {invalid_string}"
        # Test with `data_dir`
        try:
            actual = path.list_available_variables(
                source_id = 'EC-Earth3P-HR',
                data_dir = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`list_available_variables` raised an exception on invalid `data_dir`: {e}"
        else:
            assert False, f"`list_available_variables` did not raise an exception on invalid `data_dir` {invalid_string}"
        # Test with `project`
        try:
            actual = path.list_available_variables(
                source_id = 'EC-Earth3P-HR',
                project = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`list_available_variables` raised an exception on invalid `project`: {e}"
        else:
            assert False, f"`list_available_variables` did not raise an exception on invalid `project` {invalid_string}"
        # Test with `activity_id`
        try:
            actual = path.list_available_variables(
                source_id = 'EC-Earth3P-HR',
                activity_id = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`list_available_variables` raised an exception on invalid `activity_id`: {e}"
        else:
            assert False, f"`list_available_variables` did not raise an exception on invalid `activity_id` {invalid_string}"

def test_get_variable_path():
    """Test the `get_variable_path` function."""
    # Define test cases that should not raise warnings
    ## Note: The expected output of these test cases is manually kept up to date
    test_cases = [
        {
            'source_id': 'AWI-CM-1-1-HR',
            'variable_id': 'areacello',
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/AWI/AWI-CM-1-1-HR/hist-1950/r1i1p1f2/Ofx/areacello'
        },
        {
            'source_id': 'AWI-CM-1-1-HR',
            'variable_id': 'areacello',
            'experiment_id': 'control-1950',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/AWI/AWI-CM-1-1-HR/control-1950/r1i1p1f2/Ofx/areacello'
        },
        {
            'source_id': 'AWI-CM-1-1-LR',
            'variable_id': 'areacello',
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/AWI/AWI-CM-1-1-LR/hist-1950/r1i1p1f2/Ofx/areacello'
        },
        {
            'source_id': 'BCC-CSM2-HR',
            'variable_id': 'areacello',
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/BCC/BCC-CSM2-HR/hist-1950/r1i1p1f1/Ofx/areacello'
        },
        {
            'source_id': 'CESM1-CAM5-SE-HR',
            'variable_id': 'areacello',
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/NCAR/CESM1-CAM5-SE-HR/hist-1950/r1i1p1f1/Ofx/areacello'
        },
        {
            'source_id': 'CESM1-CAM5-SE-LR',
            'variable_id': 'areacello',
            'experiment_id': 'control-1950',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/NCAR/CESM1-CAM5-SE-LR/control-1950/r1i1p1f1/Ofx/areacello'
        },
        {
            'source_id': 'EC-Earth3P',
            'variable_id': 'areacello',
            'experiment_id': 'highres-future',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P/highres-future/r2i1p2f1/Ofx/areacello'
        },
        {
            'source_id': 'EC-Earth3P-HR',
            'variable_id': 'areacello',
            'experiment_id': 'highres-future',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/highres-future/r2i1p2f1/Ofx/areacello'
        },
        {
            'source_id': 'EC-Earth3P-HR',
            'variable_id': 'siage',
            'experiment_id': 'hist-1950',
            'variant_label': 'r2i1p2f1',
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r2i1p2f1/SImon/siage'
        },
        {
            'source_id': 'EC-Earth3P-HR',
            'variable_id': 'siu',
            'experiment_id': 'hist-1950',
            'variant_label': 'r3i1p2f1',
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/siu'
        },
        {
            'source_id': 'HadGEM3-GC31-HM',
            'variable_id': 'areacello',
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-HM/hist-1950/r1i1p1f1/Ofx/areacello'
        },
        {
            'source_id': 'HadGEM3-GC31-HM',
            'variable_id': 'areacello',
            'experiment_id': 'highres-future',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-HM/highres-future/r1i1p1f1/Ofx/areacello'
        },
        {
            'source_id': 'HadGEM3-GC31-HM',
            'variable_id': 'areacello',
            'experiment_id': 'control-1950',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-HM/control-1950/r1i1p1f1/Ofx/areacello'
        },
        {
            'source_id': 'HadGEM3-GC31-LL',
            'variable_id': 'areacello',
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-LL/hist-1950/r1i1p1f1/Ofx/areacello'
        },
        {
            'source_id': 'HadGEM3-GC31-LL',
            'variable_id': 'areacello',
            'experiment_id': 'highres-future',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-LL/highres-future/r1i1p1f1/Ofx/areacello'
        },
        {
            'source_id': 'HadGEM3-GC31-LL',
            'variable_id': 'areacello',
            'experiment_id': 'control-1950',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-LL/control-1950/r1i1p1f1/Ofx/areacello'
        },
        {
            'source_id': 'HadGEM3-GC31-LL',
            'variable_id': 'areacello',
            'experiment_id': 'spinup-1950',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-LL/spinup-1950/r1i1p1f1/Ofx/areacello'
        },
        {
            'source_id': 'HadGEM3-GC31-MM',
            'variable_id': 'areacello',
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/Ofx/areacello'
        },
        {
            'source_id': 'HadGEM3-GC31-MM',
            'variable_id': 'areacello',
            'experiment_id': 'highres-future',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/highres-future/r1i1p1f1/Ofx/areacello'
        },
        {
            'source_id': 'HadGEM3-GC31-MM',
            'variable_id': 'areacello',
            'experiment_id': 'control-1950',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/control-1950/r1i1p1f1/Ofx/areacello'
        },
        {
            'source_id': 'HadGEM3-GC31-MM',
            'variable_id': 'areacello',
            'experiment_id': 'spinup-1950',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/spinup-1950/r1i1p1f1/Ofx/areacello'
        },
    ]
    for test_case in test_cases:
        actual = path.get_variable_path(
            source_id=test_case['source_id'], 
            variable_id=test_case['variable_id'],
            experiment_id=test_case['experiment_id'],
            variant_label=test_case['variant_label'],
        )
        assert actual == test_case['expected_path'], f"`get_variable_path` failed on test case: {test_case}. \nExpected: {test_case['expected_path']} \nActual: {actual}"

    # Define test cases that should raise warnings
    ## Note: The expected output of these test cases is manually kept up to date
    test_cases = [
        {
            'source_id': 'EC-Earth3P-HR',
            'variable_id': 'siage',
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siage'
        },
        {
            'source_id': 'EC-Earth3P-HR',
            'variable_id': 'siconc',
            'experiment_id': 'hist-1950',
            'variant_label': None,
            'expected_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc'
        },
    ]
    for test_case in test_cases:
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            # Trigger a warning.
            actual = path.get_variable_path(
                source_id=test_case['source_id'], 
                variable_id=test_case['variable_id'],
                experiment_id=test_case['experiment_id'],
                variant_label=test_case['variant_label'],
            )
            assert actual == test_case['expected_path'], f"`get_variable_path` failed on test case: {test_case}."
            # Verify a warning was triggered
            assert len(w) == 1, f"`get_variable_path` did not trigger a warning on the test case {test_case}"
            # Verify the type of that warning
            assert issubclass(w[-1].category, UserWarning), f"`get_variable_path` did not trigger a `UserWarning` warning on the test case {test_case}. \nGot: {w[-1].category}"
            # Verify the warning message contains the expected text
            assert "More than one file path found" in str(w[-1].message), f"`get_variable_path` did not trigger a warning with the expected message on the test case {test_case}. \nGot: {w[-1].message}"

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
            actual = path.get_variable_path(
                source_id = invalid_test_case['source_id'],
                variable_id = invalid_test_case['variable_id'],
                experiment_id = invalid_test_case['experiment_id'],
                variant_label = invalid_test_case['variant_label'],
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`get_variable_path` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`get_variable_path` did not raise an exception on invalid test case {invalid_test_case}"
    
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
            actual = path.get_variable_path(
                source_id = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`get_variable_path` raised an exception on invalid `source_id`: {e}"
        else:
            assert False, f"`get_variable_path` did not raise an exception on invalid `source_id` {invalid_string}"
        # Test with `variable_id`
        try:
            actual = path.get_variable_path(
                variable_id = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`get_variable_path` raised an exception on invalid `variable_id`: {e}"
        else:
            assert False, f"`get_variable_path` did not raise an exception on invalid `variable_id` {invalid_string}"
        # Test with `experiment_id`
        try:
            actual = path.get_variable_path(
                experiment_id = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`get_variable_path` raised an exception on invalid `experiment_id`: {e}"
        else:
            assert False, f"`get_variable_path` did not raise an exception on invalid `experiment_id` {invalid_string}"
        # Test with `variant_label`
        if not isinstance(invalid_string, type(None)):
            try:
                actual = path.get_variable_path(
                    variant_label = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`get_variable_path` raised an exception on invalid `variant_label`: {e}"
            else:
                assert False, f"`get_variable_path` did not raise an exception on invalid `variant_label` {invalid_string}"

def test_list_variable_modifications():
    """Test the `list_variable_modifications` function."""
    # Define test cases
    ## Note: The expected output of these test cases is manually kept up to date
    test_cases = [
        {
            'variable_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/AWI/AWI-CM-1-1-HR/hist-1950/r1i1p1f2/Ofx/areacello',
            'list_filenames': True,
            'expected_dict': {
                '': ['areacello_Ofx_AWI-CM-1-1-HR_hist-1950_r1i1p1f2_gn.nc'],
            },
        },
        {
            'variable_path': '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r2i1p2f1/SImon/siconc',
            'list_filenames': False,
            'expected_dict': {
                '': 65,
                'trim_NWP_': 65,
            },
        },
    ]
    for test_case in test_cases:
        actual = path.list_variable_modifications(
            variable_path=test_case['variable_path'], 
            list_filenames=test_case['list_filenames'],
        )
        assert actual == test_case['expected_dict'], f"`list_variable_modifications` failed on test case: {test_case}. \nExpected: {test_case['expected_dict']} \nActual: {actual}"

    # Define invalid test cases
    invalid_test_cases = [
        {
            'variable_path': 'src',
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = path.list_variable_modifications(
                variable_path = invalid_test_case['variable_path'],
            )
        except (FileNotFoundError, ValueError) as e:
            assert True, f"`list_variable_modifications` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`list_variable_modifications` did not raise an exception on invalid test case {invalid_test_case}"
    
    # Define a list of invalid strings
    invalid_strings = [
        1234,
        3.14,
        None,
        [],
        {}
    ]
    for invalid_string in invalid_strings:
        # Test with `variable_path`
        try:
            actual = path.list_variable_modifications(
                variable_path = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`list_variable_modifications` raised an exception on invalid `variable_path`: {e}"
        else:
            assert False, f"`list_variable_modifications` did not raise an exception on invalid `variable_path` {invalid_string}"
        # Test with `list_filenames`
        try:
            actual = path.list_variable_modifications(
                list_filenames = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`list_variable_modifications` raised an exception on invalid `list_filenames`: {e}"
        else:
            assert False, f"`list_variable_modifications` did not raise an exception on invalid `list_filenames` {invalid_string}"
