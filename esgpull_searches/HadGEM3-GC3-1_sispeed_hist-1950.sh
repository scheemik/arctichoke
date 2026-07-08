uv run esgpull search \
project:CMIP6 \
activity_id:HighResMIP \
data_node:eagle.alcf.anl.gov,esgf-node.ornl.gov \
experiment_id:hist-1950 \
source_id:HadGEM3-GC31-HH,HadGEM3-GC31-HM,HadGEM3-GC31-MM \
frequency:mon \
variable_id:sispeed
# Expect to find 14 datasets.
# Downloads 455 files (21.9 GiB)