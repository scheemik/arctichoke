uv run esgpull search \
project:CMIP6 \
activity_id:HighResMIP \
data_node:eagle.alcf.anl.gov,esgf-node.ornl.gov \
experiment_id:hist-1950 \
source_id:EC-Earth3P-HR \
frequency:mon \
variable_id:siage,siconc,sispeed,sithick,siu,siv,sivol
# Expect to find 42 datasets.
# Downloads 1365 files (33.4 GiB)