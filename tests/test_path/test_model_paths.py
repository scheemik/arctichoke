import warnings
warnings.filterwarnings("error")

from seaicecp import path

def test_list_available_models():
    """Test the `list_available_models` function."""
    # Define test cases
    ## Note: The expected output of these test cases is manually kept up to date
    test_cases = [
        {
            'institution_id': None,
            'expected_models': [
                'AWI/AWI-CM-1-1-HR',
                'AWI/AWI-CM-1-1-LR',
                'BCC/BCC-CSM2-HR',
                'EC-Earth-Consortium/EC-Earth3P',
                'EC-Earth-Consortium/EC-Earth3P-HR',
                'MOHC/HadGEM3-GC31-HH',
                'MOHC/HadGEM3-GC31-HM',
                'MOHC/HadGEM3-GC31-LL',
                'MOHC/HadGEM3-GC31-MM',
                'NCAR/CESM1-CAM5-SE-HR',
                'NCAR/CESM1-CAM5-SE-LR',
                'NERC/HadGEM3-GC31-HH',
                'NERC/HadGEM3-GC31-HM'
            ],
        },
        {
            'institution_id': 'EC-Earth-Consortium',
            'expected_models': ['EC-Earth-Consortium/EC-Earth3P', 'EC-Earth-Consortium/EC-Earth3P-HR'],
        },
        {
            'institution_id': ['MOHC','NERC'],
            'expected_models': [
                'MOHC/HadGEM3-GC31-HH',
                'MOHC/HadGEM3-GC31-HM',
                'MOHC/HadGEM3-GC31-LL',
                'MOHC/HadGEM3-GC31-MM',
                'NERC/HadGEM3-GC31-HH',
                'NERC/HadGEM3-GC31-HM'
            ],
        },
    ]
    for test_case in test_cases:
        actual = path.list_available_models(institution_id=test_case['institution_id'])
        assert actual == test_case['expected_models'], f"`list_available_models` failed on test case: {test_case}.\nHas the expected list in `tests/test_path/test_find_data.py` been updated?"

    # Define invalid test cases
    invalid_test_cases = [
        {
            'data_dir': 'invalid_string',
            'project': 'CMIP6',
            'activity_id': 'HighResMIP',
            'institution_id': None,
        },
        {
            'data_dir': '/seaicecp_data/bergybits/data',
            'project': 'invalid_string',
            'activity_id': 'HighResMIP',
            'institution_id': None,
        },
        {
            'data_dir': '/seaicecp_data/bergybits/data',
            'project': 'CMIP6',
            'activity_id': 'invalid_string',
            'institution_id': None,
        },
        {
            'data_dir': '/seaicecp_data/bergybits/data',
            'project': 'CMIP6',
            'activity_id': 'HighResMIP',
            'institution_id': 'invalid_string',
        },
    ]
    for invalid_test_case in invalid_test_cases:
        try:
            actual = path.list_available_models(
                data_dir = invalid_test_case['data_dir'],
                project = invalid_test_case['project'],
                activity_id = invalid_test_case['activity_id'],
                institution_id = invalid_test_case['institution_id'],
            )
        except (FileNotFoundError) as e:
            assert True, f"`list_available_models` raised an exception on invalid test case: {e}"
        else:
            assert False, f"`list_available_models` did not raise an exception on invalid test case {invalid_test_case}"
    
    # Define a list of invalid strings
    invalid_strings = [
        1234,
        3.14,
        None,
        [],
        {}
    ]
    for invalid_string in invalid_strings:
        # Test with `data_dir`
        try:
            actual = path.list_available_models(
                data_dir = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`list_available_models` raised an exception on invalid `data_dir`: {e}"
        else:
            assert False, f"`list_available_models` did not raise an exception on invalid `data_dir` {invalid_string}"
        # Test with `project`
        try:
            actual = path.list_available_models(
                project = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`list_available_models` raised an exception on invalid `project`: {e}"
        else:
            assert False, f"`list_available_models` did not raise an exception on invalid `project` {invalid_string}"
        # Test with `activity_id`
        try:
            actual = path.list_available_models(
                activity_id = invalid_string,
            )
        except (TypeError) as e:
            assert True, f"`list_available_models` raised an exception on invalid `activity_id`: {e}"
        else:
            assert False, f"`list_available_models` did not raise an exception on invalid `activity_id` {invalid_string}"
        # Test with `institution_id`
        if not isinstance(invalid_string, (type(None), type([]))):
            try:
                actual = path.list_available_models(
                    institution_id = invalid_string,
                )
            except (TypeError) as e:
                assert True, f"`list_available_models` raised an exception on invalid `institution_id`: {e}"
            else:
                assert False, f"`list_available_models` did not raise an exception on invalid `institution_id` {invalid_string}"

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
        assert actual == test_case['expected_path'], f"`get_model_path` failed on test case: {test_case}. \nExpected: {test_case['expected_path']} \nActual: {actual}"

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
