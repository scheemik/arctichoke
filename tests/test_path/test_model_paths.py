import warnings
warnings.filterwarnings("error")

from seaicecp import path

def test_get_model_path():
    """Test the `get_model_path` function."""
    # Define test cases
    ## Note: The expected output of these test cases is manually kept up to date
    test_cases = [
        {
            'source_id': 'AWI-CM-1-1-HR',
            'expected_path': ['/seaicecp_data/bergybits/data/CMIP6/HighResMIP/AWI/AWI-CM-1-1-HR']
        },
        {
            'source_id': 'AWI-CM-1-1-LR',
            'expected_path': ['/seaicecp_data/bergybits/data/CMIP6/HighResMIP/AWI/AWI-CM-1-1-LR']
        },
        {
            'source_id': 'BCC-CSM2-HR',
            'expected_path': ['/seaicecp_data/bergybits/data/CMIP6/HighResMIP/BCC/BCC-CSM2-HR']
        },
        {
            'source_id': 'CESM1-CAM5-SE-HR',
            'expected_path': ['/seaicecp_data/bergybits/data/CMIP6/HighResMIP/NCAR/CESM1-CAM5-SE-HR']
        },
        {
            'source_id': 'CESM1-CAM5-SE-LR',
            'expected_path': ['/seaicecp_data/bergybits/data/CMIP6/HighResMIP/NCAR/CESM1-CAM5-SE-LR']
        },
        {
            'source_id': 'EC-Earth3P',
            'expected_path': ['/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P']

        },
        {
            'source_id': 'EC-Earth3P-HR',
            'expected_path': ['/seaicecp_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR']

        },
        {
            'source_id': 'HadGEM3-GC31-HH',
            'expected_path': [
                '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-HH',
                '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/NERC/HadGEM3-GC31-HH',
            ]
        },
        {
            'source_id': 'HadGEM3-GC31-HM',
            'expected_path': [
                '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-HM',
                '/seaicecp_data/bergybits/data/CMIP6/HighResMIP/NERC/HadGEM3-GC31-HM',
            ]
        },
        {
            'source_id': 'HadGEM3-GC31-LL',
            'expected_path': ['/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-LL']
        },
        {
            'source_id': 'HadGEM3-GC31-MM',
            'expected_path': ['/seaicecp_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM']
        },
    ]
    for test_case in test_cases:
        actual = path.get_model_path(source_id=test_case['source_id'])
        assert actual == test_case['expected_path'], f"`get_model_path` failed on test case: {test_case}."

    # Define invalid test cases
    invalid_test_cases = [
        {
            'source_id': 'invalid_string',
            'data_dir': '/seaicecp_data/bergybits/data',
            'project': 'CMIP6',
            'activity_id': 'HighResMIP',
        },
        {
            'source_id': 'HadGEM3-GC31-HM',
            'data_dir': 'invalid_string',
            'project': 'CMIP6',
            'activity_id': 'HighResMIP',
        },
        {
            'source_id': 'HadGEM3-GC31-HM',
            'data_dir': '/seaicecp_data/bergybits/data',
            'project': 'invalid_string',
            'activity_id': 'HighResMIP',
        },
        {
            'source_id': 'HadGEM3-GC31-HM',
            'data_dir': '/seaicecp_data/bergybits/data',
            'project': 'CMIP6',
            'activity_id': 'invalid_string',
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = path.get_model_path(
                source_id = invalid_test_case['source_id'],
                data_dir = invalid_test_case['data_dir'],
                project = invalid_test_case['project'],
                activity_id = invalid_test_case['activity_id'],
            )
        except (FileNotFoundError) as e:
            assert True, f"`get_model_path` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`get_model_path` did not raise an exception on invalid test case {invalid_test_case}"
    
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
            actual = path.get_model_path(
                source_id = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`get_model_path` raised an exception on invalid `source_id`: {e}"
        else:
            assert False, f"`get_model_path` did not raise an exception on invalid `source_id` {invalid_string}"
        # Test with `data_dir`
        try:
            actual = path.get_model_path(
                data_dir = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`get_model_path` raised an exception on invalid `data_dir`: {e}"
        else:
            assert False, f"`get_model_path` did not raise an exception on invalid `data_dir` {invalid_string}"
        # Test with `project`
        try:
            actual = path.get_model_path(
                project = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`get_model_path` raised an exception on invalid `project`: {e}"
        else:
            assert False, f"`get_model_path` did not raise an exception on invalid `project` {invalid_string}"
        # Test with `activity_id`
        try:
            actual = path.get_model_path(
                activity_id = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`get_model_path` raised an exception on invalid `activity_id`: {e}"
        else:
            assert False, f"`get_model_path` did not raise an exception on invalid `activity_id` {invalid_string}"

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
        assert actual == test_case['expected_path'], f"`get_variable_path` failed on test case: {test_case}."

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
