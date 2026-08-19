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

# Canadian Arctic Archipelago Region for plotting a map
CAAM_LAT_MAX = 90
CAAM_LAT_MIN = 58
CAAM_LON_MAX = -30
CAAM_LON_MIN = -140
CAAM_BBOX = [CAAM_LAT_MAX, CAAM_LAT_MIN, CAAM_LON_MAX, CAAM_LON_MIN]

# Nares Strait
NS_LAT_MAX = 82
NS_LAT_MIN = 78.4
NS_LON_MAX = -59
NS_LON_MIN = -77
NS_BBOX = [NS_LAT_MAX, NS_LAT_MIN, NS_LON_MAX, NS_LON_MIN]

# Parry Channel
PC_LAT_MAX = 75
PC_LAT_MIN = 73.5
PC_LON_MAX = -80
PC_LON_MIN = -120
PC_BBOX = [PC_LAT_MAX, PC_LAT_MIN, PC_LON_MAX, PC_LON_MIN]

# Test Region
TEST_LAT_MAX = 80
TEST_LAT_MIN = 79
TEST_LON_MAX = -70
TEST_LON_MIN = -75
TEST_BBOX = [TEST_LAT_MAX, TEST_LAT_MIN, TEST_LON_MAX, TEST_LON_MIN]