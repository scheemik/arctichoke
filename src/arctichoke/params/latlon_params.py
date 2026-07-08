# Define coordinate values for particular places

# All bounding boxes will be defined in this order:
# [LAT_MAX, LAT_MIN, LON_MAX, LON_MIN]

# Northwest Passage Region
# "The Northwest Passage (NWP) region covers the area between 170°W–80°W and 65°N–77°N, ..." Saenko et al. 2025 (on page 2)
NWP_LAT_MAX = 77
NWP_LAT_MIN = 65
NWP_LON_MAX = -80
NWP_LON_MIN = -170
NWP_BBOX = [NWP_LAT_MAX, NWP_LAT_MIN, NWP_LON_MAX, NWP_LON_MIN]

# Canadian Arctic Archipelago Region
CAA_LAT_MAX = 85
CAA_LAT_MIN = 65
CAA_LON_MAX = -15
CAA_LON_MIN = -130
CAA_BBOX = [CAA_LAT_MAX, CAA_LAT_MIN, CAA_LON_MAX, CAA_LON_MIN]

# Test Region
TEST_LAT_MAX = 80
TEST_LAT_MIN = 79
TEST_LON_MAX = -70
TEST_LON_MIN = -75
TEST_BBOX = [TEST_LAT_MAX, TEST_LAT_MIN, TEST_LON_MAX, TEST_LON_MIN]