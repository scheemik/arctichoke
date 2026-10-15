# Investigating specific regions

Below, I describe how I investigate the specific regions of the Nares Strait and Parry Channel.
This assumes you have already gone through {doc}`Trimming data to the CAA region <../docs_data/trim_to_CAA_region>` and {doc}`Making sea ice climatologies <../docs_analysis/climatologies>`.

## Contents

- [Defining specific regions](#defining-specific-regions)
    - [Defining the Nares Strait region](#defining-the-nares-strait-region)
    - [Defining the Parry Channel region](#defining-the-parry-channel-region)
    - [Defining the Queen Elizabeth Islands regions](#defining-the-queen-elizabeth-islands-regions)
- [Trimming data to specific regions](#trimming-data-to-specific-regions)
    - [Trimming data to Nares Strait](#trimming-data-to-nares-strait)
        - [Trimming EC-Earth3P-HR data to Nares Strait](#trimming-ec-earth3p-hr-data-to-nares-strait)
        - [Trimming HadGEM3-GC31 data to Nares Strait](#trimming-hadgem3-gc31-mm-data-to-nares-strait)
    - [Trimming data to Parry Channel](#trimming-data-to-parry-channel)
        - [Trimming EC-Earth3P-HR data to Parry Channel](#trimming-ec-earth3p-hr-data-to-parry-channel)
        - [Trimming HadGEM3-GC31 data to Parry Channel](#trimming-hadgem3-gc31-mm-data-to-parry-channel)
    - [Trimming data to QEI West](#trimming-data-to-qei-west)
        - [Trimming EC-Earth3P-HR data to QEI West](#trimming-ec-earth3p-hr-data-to-qei-west)
    - [Trimming data to QEI East](#trimming-data-to-qei-east)
        - [Trimming EC-Earth3P-HR data to QEI East](#trimming-ec-earth3p-hr-data-to-qei-east)
- [Finding spatial averages](#finding-spatial-averages)
    - [Finding spatial averages of concentration](#finding-spatial-averages-of-concentration)
    - [Finding spatial averages of concentration where thickness is > 2 m](#finding-spatial-averages-of-concentration-where-thickness-is--2-m)
- [Time series plots for specific regions](#time-series-plots-for-specific-regions)
    - [Time series plots for Nares Strait](#time-series-plots-for-nares-strait)
        - [Nares Strait time series for EC-Earth3P-HR](#nares-strait-time-series-for-ec-earth3p-hr)
        - [Nares Strait time series for HadGEM3-GC31-MM](#nares-strait-time-series-for-hadgem3-gc31-mm)
    - [Time series plots for Parry Channel](#time-series-plots-for-parry-channel)
        - [Parry Channel time series for EC-Earth3P-HR](#parry-channel-time-series-for-ec-earth3p-hr)
        - [Parry Channel time series for HadGEM3-GC31-MM](#parry-channel-time-series-for-hadgem3-gc31-mm)
    - [Time series plots for QEI West](#time-series-plots-for-qei-west)
        - [QEI West time series for EC-Earth3P-HR](#qei-west-time-series-for-ec-earth3p-hr)
    - [Time series plots for QEI East](#time-series-plots-for-qei-east)
        - [QEI East time series for EC-Earth3P-HR](#qei-east-time-series-for-ec-earth3p-hr)

---

## Defining specific regions
[back to top](#investigating-specific-regions)

For each specific region I'll investigate, I'll need to define a bounding box.

### Defining the Nares Strait region
[back to top](#investigating-specific-regions)

For this study, I'll define the Nares Strait region to go from Robeson Channel in the north to Smith Sound in the south.
On Wikipedia, [Robeson Channel](https://en.wikipedia.org/wiki/Robeson_Channel) is defined to be 82°00′N, 61°30′W, and [Smith Sound](https://en.wikipedia.org/wiki/Smith_Sound) is defined to be 78°25′N, 74°00′W.
I'll use those latitude values and define the longitude bounds to be wide enough to cover the entire channel, but narrow enough to not include anything outside the channel.
I define the bounding box for Nares Strait in the `params` module.
```python
from arctichoke.params import NS_BBOX

NS_BBOX
```
```console
[82, 78.4, -59, -77]
```

As an example, I'll load a `siconc` file from `EC-Earth3P-HR` and trim it to the Nares Strait region.
Then, I'll plot just that data for January 1950 on the map, including the `mark_bbox` argument to highlight the bounding box I selected.
```python
from arctichoke.dataset import trim_latlon
import arctichoke.params as sps

dataset = trim_latlon(
    dataset = '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_CAA_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc',
    map_bbox = sps.NS_BBOX,
    precise_trim = True,
)

from arctichoke.plot import quadmesh_map

quadmesh_map(
    dataset.isel(time=0),
    'siconc',
    mark_bbox = sps.NS_BBOX,
    clims = sps.sea_ice_vars['siconc']['plot_range'],
    add_region = False,
)
```
![EC-Earth3P-HR_r1i1p2f1_siconc_NS_1950-01_map.png](investigate_specific_regions-img/EC-Earth3P-HR_r1i1p2f1_siconc_NS_1950-01_map.png)

Next, I'll make a version of that map, but plot the climatology of sea ice concentration.
```python
import xarray as xr 

from arctichoke.dataset import select_months, trim_latlon
import arctichoke.params as sps

this_si_var = 'siconc'
dataset_clim = select_months(f'/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/{this_si_var}_month_mean/gn/v20181212/trim_CAA_{this_si_var}_month_mean_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-196912.nc', time_dim='month')
# Save the attributes for later
keep_these_attrs = dataset_clim.attrs
dataset_clim = trim_latlon(
    dataset = dataset_clim,
    map_bbox = sps.NS_BBOX,
    precise_trim = True,
)
# Put the attributes back
dataset_clim.attrs = keep_these_attrs
# Sum across the 12 months
dataset_clim = dataset_clim.mean(dim='month')
# Adjust the `long_name` attribute to change the colorbar label
dataset_clim[f'{this_si_var}_month_mean'].attrs['long_name'] = dataset_clim[f'{this_si_var}_month_mean'].attrs['long_name'].replace('onthly m', '')

from arctichoke.plot import quadmesh_map

quadmesh_map(
    dataset_clim,
    f'{this_si_var}_month_mean',
    mark_bbox = sps.NS_BBOX,
    clims = sps.sea_ice_vars[this_si_var]['plot_range'],
    add_region = False,
)
```
![EC-Earth3P-HR_r1i1p2f1_siconc_NS_clim_mean_map.png](investigate_specific_regions-img/EC-Earth3P-HR_r1i1p2f1_siconc_NS_clim_mean_map.png)

### Defining the Parry Channel region
[back to top](#investigating-specific-regions)

For this study, I am still looking to see whether I can find a citation where a bounding box for the Parry Channel is defined.
Using Cook et al. 2024 Figure 1 as a guide, I've chosen a set of coordinates which goes approximately from the M'Clure Strait in the west to Lancaster Sound in the west, and covering a north-south swath which covers most of the commonly used shipping tracks.
I define the bounding box for Parry Channel in the `params` module.
```python
from arctichoke.params import PC_BBOX

PC_BBOX
```
```console
[75, 73.5, -80, -120]
```

As an example, I'll load a `siconc` file from `EC-Earth3P-HR` and trim it to the Parry Channel region.
Then, I'll plot just that data for January 1950 on the map, including the `mark_bbox` argument to highlight the bounding box I selected.
```python
from arctichoke.dataset import trim_latlon
import arctichoke.params as sps

dataset = trim_latlon(
    dataset = '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_CAA_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc',
    map_bbox = sps.PC_BBOX,
    precise_trim = True,
)

from arctichoke.plot import quadmesh_map

quadmesh_map(
    dataset.isel(time=0),
    'siconc',
    map_bbox=sps.PC_BBOX,
    mark_bbox=True,
    clims = sps.sea_ice_vars['siconc']['plot_range'],
    add_region = False,
)
```
![EC-Earth3P-HR_r1i1p2f1_siconc_PC_1950-01_map.png](investigate_specific_regions-img/EC-Earth3P-HR_r1i1p2f1_siconc_PC_1950-01_map.png)

Next, I'll make a version of that map, but plot the climatology of sea ice concentration.
```python
import xarray as xr 

from arctichoke.dataset import select_months, trim_latlon
import arctichoke.params as sps

this_si_var = 'siconc'
dataset_clim = select_months(f'/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/{this_si_var}_month_mean/gn/v20181212/trim_CAA_{this_si_var}_month_mean_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-196912.nc', time_dim='month')
# Save the attributes for later
keep_these_attrs = dataset_clim.attrs
dataset_clim = trim_latlon(
    dataset = dataset_clim,
    map_bbox = sps.PC_BBOX,
    precise_trim = True,
)
# Put the attributes back
dataset_clim.attrs = keep_these_attrs
# Sum across the 12 months
dataset_clim = dataset_clim.mean(dim='month')
# Adjust the `long_name` attribute to change the colorbar label
dataset_clim[f'{this_si_var}_month_mean'].attrs['long_name'] = dataset_clim[f'{this_si_var}_month_mean'].attrs['long_name'].replace('onthly m', '')

from arctichoke.plot import quadmesh_map

quadmesh_map(
    dataset_clim,
    f'{this_si_var}_month_mean',
    map_bbox = sps.PC_BBOX,
    mark_bbox = True,
    clims = sps.sea_ice_vars[this_si_var]['plot_range'],
    add_region = False,
)
```
![EC-Earth3P-HR_r1i1p2f1_siconc_PC_clim_mean_map.png](investigate_specific_regions-img/EC-Earth3P-HR_r1i1p2f1_siconc_PC_clim_mean_map.png)

### Defining the Queen Elizabeth Islands regions
[back to top](#investigating-specific-regions)

For this study, I am still looking to see whether I can find a citation where a bounding box for the Queen Elizabeth Islands (QEI) is defined.
I'm using Howell and Brady 2019 Figure 1 as a guide for defining the QEI West region.
I define the bounding box for the QEI West region in the `params` module.
```python
from arctichoke.params import QW_BBOX

QW_BBOX
```
```
[79, 75, -95, -118]
```

As an example, I'll load a `siconc` file from `EC-Earth3P-HR` and trim it to the QEI West region.
Then, I'll plot just that data for January 1950 on the map, including the `mark_bbox` argument to highlight the bounding box I selected.
```python
from arctichoke.dataset import trim_latlon
import arctichoke.params as sps

dataset = trim_latlon(
    dataset = '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_CAA_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc',
    map_bbox = sps.QW_BBOX,
    precise_trim = True,
)

from arctichoke.plot import quadmesh_map

this_map = quadmesh_map(
    dataset.isel(time=0),
    'siconc',
    map_bbox = sps.QW_BBOX,
    mark_bbox = True,
    clims = sps.sea_ice_vars['siconc']['plot_range'],
    add_region = False,
)
display(this_map)
```
![EC-Earth3P-HR_r1i1p2f1_siconc_QW_1950-01_map.png](investigate_specific_regions-img/EC-Earth3P-HR_r1i1p2f1_siconc_QW_1950-01_map.png)

Next, I'll make a version of that map, but plot the climatology of sea ice concentration.
```python
import xarray as xr 

from arctichoke.dataset import select_months, trim_latlon
import arctichoke.params as sps

this_si_var = 'siconc'
dataset_clim = select_months(f'/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/{this_si_var}_month_mean/gn/v20181212/trim_CAA_{this_si_var}_month_mean_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-196912.nc', time_dim='month')
# Save the attributes for later
keep_these_attrs = dataset_clim.attrs
dataset_clim = trim_latlon(
    dataset = dataset_clim,
    map_bbox = sps.QW_BBOX,
    precise_trim = True,
)
# Put the attributes back
dataset_clim.attrs = keep_these_attrs
# Sum across the 12 months
dataset_clim = dataset_clim.mean(dim='month')
# Adjust the `long_name` attribute to change the colorbar label
dataset_clim[f'{this_si_var}_month_mean'].attrs['long_name'] = dataset_clim[f'{this_si_var}_month_mean'].attrs['long_name'].replace('onthly m', '')

from arctichoke.plot import quadmesh_map

quadmesh_map(
    dataset_clim,
    f'{this_si_var}_month_mean',
    map_bbox = sps.QW_BBOX,
    mark_bbox = True,
    clims = sps.sea_ice_vars[this_si_var]['plot_range'],
    add_region = False,
)
```
![EC-Earth3P-HR_r1i1p2f1_siconc_QW_clim_mean_map.png](investigate_specific_regions-img/EC-Earth3P-HR_r1i1p2f1_siconc_QW_clim_mean_map.png)

I define the bounding box for the QEI East region in the `params` module.
```python
from arctichoke.params import QE_BBOX

QE_BBOX
```
```
[82, 75, -79, -95]
```

As an example, I'll load a `siconc` file from `EC-Earth3P-HR` and trim it to the QEI East region.
Then, I'll plot just that data for January 1950 on the map, including the `mark_bbox` argument to highlight the bounding box I selected.
```python
from arctichoke.dataset import trim_latlon
import arctichoke.params as sps

dataset = trim_latlon(
    dataset = '/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_CAA_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc',
    map_bbox = sps.QE_BBOX,
    precise_trim = True,
)

from arctichoke.plot import quadmesh_map

this_map = quadmesh_map(
    dataset.isel(time=0),
    'siconc',
    map_bbox = sps.QE_BBOX,
    mark_bbox = True,
    clims = sps.sea_ice_vars['siconc']['plot_range'],
    add_region = False,
)
display(this_map)
```
![EC-Earth3P-HR_r1i1p2f1_siconc_QE_1950-01_map.png](investigate_specific_regions-img/EC-Earth3P-HR_r1i1p2f1_siconc_QE_1950-01_map.png)

Next, I'll make a version of that map, but plot the climatology of sea ice concentration.
```python
import xarray as xr 

from arctichoke.dataset import select_months, trim_latlon
import arctichoke.params as sps

this_si_var = 'siconc'
dataset_clim = select_months(f'/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/{this_si_var}_month_mean/gn/v20181212/trim_CAA_{this_si_var}_month_mean_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-196912.nc', time_dim='month')
# Save the attributes for later
keep_these_attrs = dataset_clim.attrs
dataset_clim = trim_latlon(
    dataset = dataset_clim,
    map_bbox = sps.QE_BBOX,
    precise_trim = True,
)
# Put the attributes back
dataset_clim.attrs = keep_these_attrs
# Sum across the 12 months
dataset_clim = dataset_clim.mean(dim='month')
# Adjust the `long_name` attribute to change the colorbar label
dataset_clim[f'{this_si_var}_month_mean'].attrs['long_name'] = dataset_clim[f'{this_si_var}_month_mean'].attrs['long_name'].replace('onthly m', '')

from arctichoke.plot import quadmesh_map

quadmesh_map(
    dataset_clim,
    f'{this_si_var}_month_mean',
    map_bbox = sps.QE_BBOX,
    mark_bbox = True,
    clims = sps.sea_ice_vars[this_si_var]['plot_range'],
    add_region = False,
)
```
![EC-Earth3P-HR_r1i1p2f1_siconc_QE_clim_mean_map.png](investigate_specific_regions-img/EC-Earth3P-HR_r1i1p2f1_siconc_QE_clim_mean_map.png)

---

## Trimming data to specific regions
[back to top](#investigating-specific-regions)

In order to more easily call up data for these specific regions later, I'll use my `trim_files()` function to save the trimmed datasets to files.

### Trimming data to Nares Strait
[back to top](#investigating-specific-regions)

#### Trimming EC-Earth3P-HR data to Nares Strait
[back to top](#investigating-specific-regions)

I can trim the data for `EC-Earth3P-HR` to the Nares Strait region.
This takes about 40 minutes to complete.
```python
import xarray as xr

from arctichoke.dataset import trim_files
from arctichoke.params import NS_BBOX
from arctichoke.path import list_variable_files

this_model = 'EC-Earth3P-HR'

for this_variant_label in [
    'r1i1p2f1', 
    'r2i1p2f1', 
    'r3i1p2f1',
]:
    for si_var in [
        'siconc',
        'sispeed',
        'sithick',
    ]:
        for this_experiment in ['hist-1950']:
            sivar_list = list_variable_files(
                source_id = this_model,
                variable_id = si_var,
                experiment_id = this_experiment,
                variant_label = this_variant_label,
            )
            trim_files(
                files_to_trim = sivar_list,
                name_prefix = 'trim_NS_',
                map_bbox = NS_BBOX,
                precise_trim = True,
            )
```
```console
(trim_files) `name_prefix`: trim_NS_
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NS_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NS_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195101-195112.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_NS_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195201-195212.nc`.
    ...
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/sithick/gn/v20190214/trim_NS_sithick_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201201-201212.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/sithick/gn/v20190214/trim_NS_sithick_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201301-201312.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/sithick/gn/v20190214/trim_NS_sithick_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201401-201412.nc`.
```

When trimming the marker variables, I specify `with_modification` to be `trim_CAA_` as I only calculated `sislow`, `sipacked`, and `silandfast` over the CAA.
This takes about 20 minutes. 
```python
import xarray as xr

from arctichoke.dataset import trim_files
from arctichoke.params import NS_BBOX
from arctichoke.path import list_variable_files

this_model = 'EC-Earth3P-HR'
this_experiment = 'hist-1950'
this_modification = 'trim_CAA_'

for this_variant_label in [
    'r1i1p2f1', 
    'r2i1p2f1', 
    'r3i1p2f1',
]:
    for si_var in [
        'sislow',
        'sipacked',
        'silandfast',
    ]:
        sivar_list = list_variable_files(
            source_id = this_model,
            variable_id = si_var,
            experiment_id = this_experiment,
            variant_label = this_variant_label,
            with_modification = this_modification,
        )
        trim_files(
            files_to_trim = sivar_list,
            name_prefix = 'trim_NS_',
            map_bbox = NS_BBOX,
            precise_trim = True,
        )
```
```console
(trim_files) `name_prefix`: trim_NS_
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/sislow/gn/v20260617/trim_NS_sislow_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/sislow/gn/v20260617/trim_NS_sislow_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195101-195112.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/sislow/gn/v20260617/trim_NS_sislow_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195201-195212.nc`.
    ...
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/silandfast/gn/with_sispeed_clim/trim_NS_silandfast_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201201-201212.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/silandfast/gn/with_sispeed_clim/trim_NS_silandfast_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201301-201312.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/silandfast/gn/with_sispeed_clim/trim_NS_silandfast_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201401-201412.nc`.
```

I can use my `list_available_variables()` function to confirm how many trimmed files were created for each variable.
```python
from arctichoke.path import list_available_variables

list_available_variables(
    source_id = 'EC-Earth3P-HR',
    experiment_id = 'hist-1950',
    list_var_mods = True,
)
```
```console
{'EC-Earth-Consortium/EC-Earth3P-HR': {'hist-1950': {'r1i1p2f1': {'SImon': {
     'siu': {'': 65},
     'siv': {'': 65},
     'sithick': {'': 130, 'trim_CAA_': 65, 'trim_NS_': 65,},
     'siage': {'': 65},
     'siconc': {'': 130, 'trim_CAA_': 65, 'trim_NS_': 65,},
     'sispeed': {'': 130, 'trim_CAA_': 65, 'trim_NS_': 65,},
     'silandfast': {'trim_CAA_': 195, 'trim_NS_': 195},
     'sipacked': {'trim_CAA_': 65, 'trim_NS_': 65},
     'sislow': {'trim_CAA_': 65, 'trim_NS_': 65},
     ...
...
```

As a test, I can then use these trimmed data files to create a map of trends in a particular variable. 
I'll choose `siconc`.
```python
from arctichoke.params import NS_BBOX, sea_ice_vars
from arctichoke.plot import make_trend_map 

this_map = make_trend_map(
    this_source_id = 'EC-Earth3P-HR',
    this_var = 'siconc',
    this_variant_label = 'r1i1p2f1',
    this_modification = 'trim_NS_',
    select_summer = True,
    map_bbox = NS_BBOX,
    mark_bbox = True,
    find_mean = True,
    clims = sea_ice_vars['siconc']['trend_clims'],
    add_region = False,
    return_map = True,
    verbose = False,
)
display(this_map)
```
![EC-Earth3P-HR_r1i1p2f1_siconc_NS_JJASO_trend_map.png](investigate_specific_regions-img/EC-Earth3P-HR_r1i1p2f1_siconc_NS_JJASO_trend_map.png)

#### Trimming HadGEM3-GC31-MM data to Nares Strait
[back to top](#investigating-specific-regions)

I can trim the data for `HadGEM3-GC31-MM` to the Nares Strait region.
This takes about 40 minutes to complete.
```python
import xarray as xr

from arctichoke.dataset import trim_files
from arctichoke.params import NS_BBOX
from arctichoke.path import list_variable_files

this_model = 'HadGEM3-GC31-MM'
this_experiment = 'hist-1950'

for this_variant_label in [
    'r1i1p1f1', 
    'r1i2p1f1', 
    'r1i3p1f1',
]:
    for si_var in [
        'siconc2',
        'sispeed',
        'sithick',
    ]:
        for this_experiment in ['hist-1950']:
            sivar_list = list_variable_files(
                source_id = this_model,
                variable_id = si_var,
                experiment_id = this_experiment,
                variant_label = this_variant_label,
            )
            trim_files(
                files_to_trim = sivar_list,
                name_prefix = 'trim_NS_',
                map_bbox = NS_BBOX,
                precise_trim = True,
            )
```
```
(trim_files) `name_prefix`: trim_NS_
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/siconc2/gn/v20170928/trim_NS_siconc2_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_195001-195012.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/siconc2/gn/v20170928/trim_NS_siconc2_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_195101-195112.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/siconc2/gn/v20170928/trim_NS_siconc2_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_195201-195212.nc`.
    ...
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i3p1f1/SImon/sithick/gn/v20190710/trim_NS_sithick_SImon_HadGEM3-GC31-MM_hist-1950_r1i3p1f1_gn_201201-201212.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i3p1f1/SImon/sithick/gn/v20190710/trim_NS_sithick_SImon_HadGEM3-GC31-MM_hist-1950_r1i3p1f1_gn_201301-201312.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i3p1f1/SImon/sithick/gn/v20190710/trim_NS_sithick_SImon_HadGEM3-GC31-MM_hist-1950_r1i3p1f1_gn_201401-201412.nc`.
```

When trimming `siconc2` and the marker variables, I specify `with_modification` to be `trim_CAA_` as I only calculated `siconc2`, `sislow`, `sipacked`, and `silandfast` over the CAA.
This takes about 20 minutes. 
```python
import xarray as xr

from arctichoke.dataset import trim_files
from arctichoke.params import NS_BBOX
from arctichoke.path import list_variable_files

this_model = 'HadGEM3-GC31-MM'
this_experiment = 'hist-1950'
this_modification = 'trim_CAA_'

for this_variant_label in [
    'r1i1p1f1', 
    'r1i2p1f1', 
    'r1i3p1f1',
]:
    for si_var in [
        'sislow',
        'sipacked',
        'silandfast',
    ]:
        sivar_list = list_variable_files(
            source_id = this_model,
            variable_id = si_var,
            experiment_id = this_experiment,
            variant_label = this_variant_label,
            with_modification = this_modification,
        )
        trim_files(
            files_to_trim = sivar_list,
            name_prefix = 'trim_NS_',
            replace_prefix = this_modification,
            map_bbox = NS_BBOX,
            precise_trim = True,
        )
```
```
(trim_files) `name_prefix`: trim_NS_
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/sislow/gn/v20260617/trim_NS_trim_CAA_sislow_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_195001-195012.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/sislow/gn/v20260617/trim_NS_trim_CAA_sislow_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_195101-195112.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/sislow/gn/v20260617/trim_NS_trim_CAA_sislow_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_195201-195212.nc`.
    ...
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i3p1f1/SImon/silandfast/gn/with_sispeed_clim/trim_NS_trim_CAA_silandfast_SImon_HadGEM3-GC31-MM_hist-1950_r1i3p1f1_gn_201201-201212.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i3p1f1/SImon/silandfast/gn/with_sispeed_clim/trim_NS_trim_CAA_silandfast_SImon_HadGEM3-GC31-MM_hist-1950_r1i3p1f1_gn_201301-201312.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i3p1f1/SImon/silandfast/gn/with_sispeed_clim/trim_NS_trim_CAA_silandfast_SImon_HadGEM3-GC31-MM_hist-1950_r1i3p1f1_gn_201401-201412.nc`.
```

I can use my `list_available_variables()` function to confirm how many trimmed files were created for each variable.
```python
from arctichoke.path import list_available_variables

list_available_variables(
    source_id = 'HadGEM3-GC31-MM',
    experiment_id = 'hist-1950',
    list_var_mods = True,
)
```
```
{'MOHC/HadGEM3-GC31-MM': {'hist-1950': {'r1i1p1f1': {'Ofx': {'areacello': {'': 1}},
    'SImon': {'siu': {'': 65},
     'sithick': {'': 130, 'trim_CAA_': 65, 'trim_NS_': 65},
     'siage': {'': 65},
     'siconc': {'': 65, 'trim_NS_': 65},
     'siv': {'': 65},
     'sispeed': {'': 130, 'trim_CAA_': 65, 'trim_NS_': 65},
     'sivol': {'': 65, 'trim_CAA_': 65},
     'siconc2': {'trim_CAA_': 65, 'trim_NS_': 65},
     'silandfast': {'trim_CAA_': 195, 'trim_NS_': 195},
     'sipacked': {'trim_CAA_': 65, 'trim_NS_': 65},
     'sislow': {'trim_CAA_': 65, 'trim_NS_': 65},
     'siage2': {'trim_CAA_': 65},
     'simultiyear': {'trim_CAA_': 65},
     'siconc2_month_mean': {'trim_CAA_': 1},
     'sispeed_month_mean': {'trim_CAA_': 1},
     'sithick_month_mean': {'trim_CAA_': 1},
     'sivol_month_mean': {'trim_CAA_': 1},
     'silandfast_month_mean': {'trim_CAA_': 1},
     'sipacked_month_mean': {'trim_CAA_': 1},
     'sislow_month_mean': {'trim_CAA_': 1},
     'simultiyear_month_mean': {'trim_CAA_': 1}}},
   'r1i2p1f1': {'SImon': {'sithick': {'': 130,
      'trim_CAA_': 65,
      'trim_NS_': 65},
...
     'sivol_month_mean': {'trim_CAA_': 1},
     'silandfast_month_mean': {'trim_CAA_': 1},
     'sipacked_month_mean': {'trim_CAA_': 1},
     'sislow_month_mean': {'trim_CAA_': 1},
     'simultiyear_month_mean': {'trim_CAA_': 1}}}}}}
```

As a test, I can then use these trimmed data files to create a map of trends in a particular variable. 
I'll choose `siconc2`.
```python
from arctichoke.params import NS_BBOX, sea_ice_vars
from arctichoke.plot import make_trend_map 

this_map = make_trend_map(
    this_source_id = 'HadGEM3-GC31-MM',
    this_var = 'siconc2',
    this_variant_label = 'r1i1p1f1',
    this_modification = 'trim_NS_',
    select_summer = True,
    map_bbox = NS_BBOX,
    mark_bbox = True,
    find_mean = True,
    clims = sea_ice_vars['siconc2']['trend_clims'],
    add_region = False,
    return_map = True,
    verbose = False,
)
display(this_map)
```
![HadGEM3-GC31-MM_r1i1p1f1_siconc_NS_JJASO_trend_map.png](investigate_specific_regions-img/HadGEM3-GC31-MM_r1i1p1f1_siconc_NS_JJASO_trend_map.png)

### Trimming data to Parry Channel
[back to top](#investigating-specific-regions)

#### Trimming EC-Earth3P-HR data to Parry Channel
[back to top](#investigating-specific-regions)

I can trim the data for `EC-Earth3P-HR` to the Parry Channel region.
This takes about an hour to complete.
```python
import xarray as xr

from arctichoke.dataset import trim_files
from arctichoke.params import PC_BBOX
from arctichoke.path import list_variable_files

this_model = 'EC-Earth3P-HR'

for this_variant_label in [
    'r1i1p2f1', 
    'r2i1p2f1', 
    'r3i1p2f1',
]:
    for si_var in [
        'siconc',
        'sispeed',
        'sithick',
    ]:
        for this_experiment in ['hist-1950']:
            sivar_list = list_variable_files(
                source_id = this_model,
                variable_id = si_var,
                experiment_id = this_experiment,
                variant_label = this_variant_label,
            )
            trim_files(
                files_to_trim = sivar_list,
                name_prefix = 'trim_PC_',
                map_bbox = PC_BBOX,
                precise_trim = True,
            )
```
```console
(trim_files) `name_prefix`: trim_PC_
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_PC_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_PC_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195101-195112.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_PC_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195201-195212.nc`.
    ...
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/sithick/gn/v20190214/trim_PC_sithick_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201201-201212.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/sithick/gn/v20190214/trim_PC_sithick_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201301-201312.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/sithick/gn/v20190214/trim_PC_sithick_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201401-201412.nc`.
```

When trimming the marker variables, I specify `with_modification` to be `trim_CAA_` as I only calculated `sislow`, `sipacked`, and `silandfast` over the CAA.
This takes about 20 minutes. 
```python
import xarray as xr

from arctichoke.dataset import trim_files
from arctichoke.params import PC_BBOX
from arctichoke.path import list_variable_files

this_model = 'EC-Earth3P-HR'
this_experiment = 'hist-1950'
this_modification = 'trim_CAA_'

for this_variant_label in [
    'r1i1p2f1', 
    'r2i1p2f1', 
    'r3i1p2f1',
]:
    for si_var in [
        'sislow',
        'sipacked',
        'silandfast',
    ]:
        sivar_list = list_variable_files(
            source_id = this_model,
            variable_id = si_var,
            experiment_id = this_experiment,
            variant_label = this_variant_label,
            with_modification = this_modification,
        )
        trim_files(
            files_to_trim = sivar_list,
            name_prefix = 'trim_PC_',
            replace_prefix = this_modification,
            map_bbox = PC_BBOX,
            precise_trim = True,
        )
```
```console
(trim_files) `name_prefix`: trim_PC_
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/sislow/gn/v20260617/trim_PC_sislow_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/sislow/gn/v20260617/trim_PC_sislow_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195101-195112.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/sislow/gn/v20260617/trim_PC_sislow_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195201-195212.nc`.
    ...
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/silandfast/gn/with_sispeed_clim/trim_PC_silandfast_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201201-201212.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/silandfast/gn/with_sispeed_clim/trim_PC_silandfast_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201301-201312.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/silandfast/gn/with_sispeed_clim/trim_PC_silandfast_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201401-201412.nc`.
```

I can use my `list_available_variables()` function to confirm how many trimmed files were created for each variable.
```python
from arctichoke.path import list_available_variables

list_available_variables(
    source_id = 'EC-Earth3P-HR',
    experiment_id = 'hist-1950',
    list_var_mods = True,
)
```
```console
{'EC-Earth-Consortium/EC-Earth3P-HR': {'hist-1950': {'r1i1p2f1': {'SImon': {
     'siu': {'': 65},
     'siv': {'': 65},
     'sithick': {'': 195,
      'trim_CAA_': 65,
      'trim_NS_': 65,
      'trim_PC_': 65},
     'siage': {'': 65},
     'siconc': {'': 195,
      'trim_CAA_': 65,
      'trim_NS_': 65,
      'trim_PC_': 65},
     'sispeed': {'': 195,
      'trim_CAA_': 65,
      'trim_NS_': 65,
      'trim_PC_': 65},
     'silandfast': {'trim_CAA_': 195, 'trim_NS_': 195, 'trim_PC_': 195},
     'sivol': {'': 65, 'trim_CAA_': 65},
     'siconc2': {'trim_CAA_': 65},
     'sipacked': {'trim_CAA_': 65, 'trim_NS_': 65, 'trim_PC_': 65},
     'sislow': {'trim_CAA_': 65, 'trim_NS_': 65, 'trim_PC_': 65},
     'siage2': {'trim_CAA_': 65},
     'simultiyear': {'trim_CAA_': 65},
...
```

As a test, I can then use these trimmed data files to create a map of trends in a particular variable. 
I'll choose `siconc`.
```python
from arctichoke.params import PC_BBOX, sea_ice_vars
from arctichoke.plot import make_trend_map 

this_map = make_trend_map(
    this_source_id = 'EC-Earth3P-HR',
    this_var = 'siconc',
    this_variant_label = 'r1i1p2f1',
    this_modification = 'trim_PC_',
    select_summer = True,
    map_bbox = PC_BBOX,
    mark_bbox = True,
    find_mean = True,
    clims = sea_ice_vars['siconc']['trend_clims'],
    add_region = False,
    return_map = True,
    verbose = False,
)
display(this_map)
```
![EC-Earth3P-HR_r1i1p2f1_siconc_PC_JJASO_trend_map.png](investigate_specific_regions-img/EC-Earth3P-HR_r1i1p2f1_siconc_PC_JJASO_trend_map.png)

#### Trimming HadGEM3-GC31-MM data to Parry Channel
[back to top](#investigating-specific-regions)

I can trim the data for `HadGEM3-GC31-MM` to the Parry Channel region.
This takes about 40 minutes to complete.
```python
import xarray as xr

from arctichoke.dataset import trim_files
from arctichoke.params import PC_BBOX
from arctichoke.path import list_variable_files

this_model = 'HadGEM3-GC31-MM'
this_experiment = 'hist-1950'

for this_variant_label in [
    'r1i1p1f1', 
    'r1i2p1f1', 
    'r1i3p1f1',
]:
    for si_var in [
        'sispeed',
        'sithick',
    ]:
        for this_experiment in ['hist-1950']:
            sivar_list = list_variable_files(
                source_id = this_model,
                variable_id = si_var,
                experiment_id = this_experiment,
                variant_label = this_variant_label,
            )
            trim_files(
                files_to_trim = sivar_list,
                name_prefix = 'trim_PC_',
                map_bbox = PC_BBOX,
                precise_trim = True,
            )
```
```
(trim_files) `name_prefix`: trim_PC_
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/sispeed/gn/v20170928/trim_PC_sispeed_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_195001-195012.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/sispeed/gn/v20170928/trim_PC_sispeed_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_195101-195112.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/sispeed/gn/v20170928/trim_PC_sispeed_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_195201-195212.nc`.
    ...
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i3p1f1/SImon/sithick/gn/v20190710/trim_PC_sithick_SImon_HadGEM3-GC31-MM_hist-1950_r1i3p1f1_gn_201201-201212.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i3p1f1/SImon/sithick/gn/v20190710/trim_PC_sithick_SImon_HadGEM3-GC31-MM_hist-1950_r1i3p1f1_gn_201301-201312.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i3p1f1/SImon/sithick/gn/v20190710/trim_PC_sithick_SImon_HadGEM3-GC31-MM_hist-1950_r1i3p1f1_gn_201401-201412.nc`.
```

When trimming `siconc2` and the marker variables, I specify `with_modification` to be `trim_CAA_` as I only calculated `siconc2`, `sislow`, `sipacked`, and `silandfast` over the CAA.
```python
import xarray as xr

from arctichoke.dataset import trim_files
from arctichoke.params import PC_BBOX
from arctichoke.path import list_variable_files

this_model = 'HadGEM3-GC31-MM'
this_experiment = 'hist-1950'
this_modification = 'trim_CAA_'

for this_variant_label in [
    'r1i1p1f1', 
    'r1i2p1f1', 
    'r1i3p1f1',
]:
    for si_var in [
        'siconc2',
        'sislow',
        'sipacked',
        'silandfast',
    ]:
        sivar_list = list_variable_files(
            source_id = this_model,
            variable_id = si_var,
            experiment_id = this_experiment,
            variant_label = this_variant_label,
            with_modification = this_modification,
        )
        trim_files(
            files_to_trim = sivar_list,
            name_prefix = 'trim_PC_',
            replace_prefix = this_modification,
            map_bbox = PC_BBOX,
            precise_trim = True,
        )
```
```
(trim_files) `name_prefix`: trim_PC_
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/siconc2/gn/v20170928/trim_PC_siconc2_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_195001-195012.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/siconc2/gn/v20170928/trim_PC_siconc2_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_195101-195112.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i1p1f1/SImon/siconc2/gn/v20170928/trim_PC_siconc2_SImon_HadGEM3-GC31-MM_hist-1950_r1i1p1f1_gn_195201-195212.nc`.
...
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i3p1f1/SImon/silandfast/gn/with_sispeed_clim/trim_PC_silandfast_SImon_HadGEM3-GC31-MM_hist-1950_r1i3p1f1_gn_201201-201212.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i3p1f1/SImon/silandfast/gn/with_sispeed_clim/trim_PC_silandfast_SImon_HadGEM3-GC31-MM_hist-1950_r1i3p1f1_gn_201301-201312.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/MOHC/HadGEM3-GC31-MM/hist-1950/r1i3p1f1/SImon/silandfast/gn/with_sispeed_clim/trim_PC_silandfast_SImon_HadGEM3-GC31-MM_hist-1950_r1i3p1f1_gn_201401-201412.nc`.
```

I can use my `list_available_variables()` function to confirm how many trimmed files were created for each variable.
```python
from arctichoke.path import list_available_variables

list_available_variables(
    source_id = 'HadGEM3-GC31-MM',
    experiment_id = 'hist-1950',
    list_var_mods = True,
)
```
```
{'MOHC/HadGEM3-GC31-MM': {'hist-1950': {'r1i1p1f1': {'Ofx': {'areacello': {'': 1}},
    'SImon': {'siu': {'': 65},
     'sithick': {'': 195, 'trim_CAA_': 65, 'trim_NS_': 65, 'trim_PC_': 65},
     'siage': {'': 65},
     'siconc': {'': 65, 'trim_NS_': 65},
     'siv': {'': 65},
     'sispeed': {'': 195, 'trim_CAA_': 65, 'trim_NS_': 65, 'trim_PC_': 65},
     'sivol': {'': 65, 'trim_CAA_': 65},
     'siconc2': {'trim_CAA_': 65, 'trim_NS_': 65, 'trim_PC_': 65},
     'silandfast': {'trim_CAA_': 195, 'trim_NS_': 195, 'trim_PC_': 195},
     'sipacked': {'trim_CAA_': 65, 'trim_NS_': 65, 'trim_PC_': 65},
     'sislow': {'trim_CAA_': 65, 'trim_NS_': 65, 'trim_PC_': 65},
     'siage2': {'trim_CAA_': 65},
     'simultiyear': {'trim_CAA_': 65},
     'siconc2_month_mean': {'trim_CAA_': 1},
     'sispeed_month_mean': {'trim_CAA_': 1},
     'sithick_month_mean': {'trim_CAA_': 1},
     'sivol_month_mean': {'trim_CAA_': 1},
     'silandfast_month_mean': {'trim_CAA_': 1},
     'sipacked_month_mean': {'trim_CAA_': 1},
     'sislow_month_mean': {'trim_CAA_': 1},
     'simultiyear_month_mean': {'trim_CAA_': 1}}},
   'r1i2p1f1': {'SImon': {'sithick': {'': 195,
      'trim_CAA_': 65,
      'trim_NS_': 65,
...
     'sivol_month_mean': {'trim_CAA_': 1},
     'silandfast_month_mean': {'trim_CAA_': 1},
     'sipacked_month_mean': {'trim_CAA_': 1},
     'sislow_month_mean': {'trim_CAA_': 1},
     'simultiyear_month_mean': {'trim_CAA_': 1}}}}}}
```

As a test, I can then use these trimmed data files to create a map of trends in a particular variable. 
I'll choose `siconc2`.
```python
from arctichoke.params import PC_BBOX, sea_ice_vars
from arctichoke.plot import make_trend_map 

this_map = make_trend_map(
    this_source_id = 'HadGEM3-GC31-MM',
    this_var = 'siconc2',
    this_variant_label = 'r1i1p1f1',
    this_modification = 'trim_PC_',
    select_summer = True,
    map_bbox = PC_BBOX,
    mark_bbox = True,
    find_mean = True,
    clims = sea_ice_vars['siconc']['trend_clims'],
    add_region = False,
    return_map = True,
    verbose = False,
)
display(this_map)
```
![HadGEM3-GC31-MM_r1i1p1f1_siconc_PC_JJASO_trend_map.png](investigate_specific_regions-img/HadGEM3-GC31-MM_r1i1p1f1_siconc_PC_JJASO_trend_map.png)

### Trimming data to QEI West
[back to top](#investigating-specific-regions)

#### Trimming EC-Earth3P-HR data to QEI West
[back to top](#investigating-specific-regions)

I can trim the data for `EC-Earth3P-HR` to the QEI West region.
This takes about 45 minutes to complete.
```python
import xarray as xr

from arctichoke.dataset import trim_files
from arctichoke.params import QW_BBOX
from arctichoke.path import list_variable_files

this_model = 'EC-Earth3P-HR'

for this_variant_label in [
    'r1i1p2f1', 
    'r2i1p2f1', 
    'r3i1p2f1',
]:
    for si_var in [
        'siconc',
        'sispeed',
        'sithick',
    ]:
        for this_experiment in ['hist-1950']:
            sivar_list = list_variable_files(
                source_id = this_model,
                variable_id = si_var,
                experiment_id = this_experiment,
                variant_label = this_variant_label,
            )
            trim_files(
                files_to_trim = sivar_list,
                name_prefix = 'trim_QW_',
                map_bbox = QW_BBOX,
                precise_trim = True,
            )
```
```
(trim_files) `name_prefix`: trim_QW_
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_QW_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_QW_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195101-195112.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_QW_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195201-195212.nc`.
...
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/sithick/gn/v20190214/trim_QW_sithick_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201201-201212.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/sithick/gn/v20190214/trim_QW_sithick_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201301-201312.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/sithick/gn/v20190214/trim_QW_sithick_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201401-201412.nc`.
```

When trimming the marker variables, I specify `with_modification` to be `trim_CAA_` as I only calculated `sislow`, `sipacked`, and `silandfast` over the CAA.
This takes about 25 minutes. 
```python
import xarray as xr

from arctichoke.dataset import trim_files
from arctichoke.params import QW_BBOX
from arctichoke.path import list_variable_files

this_model = 'EC-Earth3P-HR'
this_experiment = 'hist-1950'
this_modification = 'trim_CAA_'

for this_variant_label in [
    'r1i1p2f1', 
    'r2i1p2f1', 
    'r3i1p2f1',
]:
    for si_var in [
        'sislow',
        'sipacked',
        'silandfast',
    ]:
        sivar_list = list_variable_files(
            source_id = this_model,
            variable_id = si_var,
            experiment_id = this_experiment,
            variant_label = this_variant_label,
            with_modification = this_modification,
        )
        trim_files(
            files_to_trim = sivar_list,
            name_prefix = 'trim_QW_',
            replace_prefix = this_modification,
            map_bbox = QW_BBOX,
            precise_trim = True,
        )
```
```
(trim_files) `name_prefix`: trim_QW_
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/sislow/gn/v20260617/trim_QW_sislow_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/sislow/gn/v20260617/trim_QW_sislow_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195101-195112.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/sislow/gn/v20260617/trim_QW_sislow_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195201-195212.nc`.
...
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/silandfast/gn/with_sispeed_clim/trim_QW_silandfast_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201201-201212.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/silandfast/gn/with_sispeed_clim/trim_QW_silandfast_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201301-201312.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/silandfast/gn/with_sispeed_clim/trim_QW_silandfast_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201401-201412.nc`.
```

I can use my `list_available_variables()` function to confirm how many trimmed files were created for each variable.
```python
from arctichoke.path import list_available_variables

list_available_variables(
    source_id = 'EC-Earth3P-HR',
    experiment_id = 'hist-1950',
    list_var_mods = True,
)
```
```
{'EC-Earth-Consortium/EC-Earth3P-HR': {'hist-1950': {'r1i1p2f1': {'SImon': {'siu': {'': 65},
     'siv': {'': 65},
     'sithick': {'': 390,
      'trim_CAA_': 65,
      'trim_NS_': 65,
      'trim_NWP_': 65,
      'trim_PC_': 65,
      'trim_QW_': 65},
     'siage': {'': 65},
     'siconc': {'': 390,
      'trim_CAA_': 65,
      'trim_NS_': 65,
      'trim_NWP_': 65,
      'trim_PC_': 65,
      'trim_QW_': 65},
     'sispeed': {'': 390,
      'trim_CAA_': 65,
      'trim_NS_': 65,
      'trim_NWP_': 65,
      'trim_PC_': 65,
      'trim_QW_': 65},
     'silandfast': {'trim_CAA_': 195,
...
```

As a test, I can then use these trimmed data files to create a map of trends in a particular variable. 
I'll choose `siconc`.
```python
from arctichoke.params import QW_BBOX
from arctichoke.plot import make_trend_map 

this_map = make_trend_map(
    this_source_id = 'EC-Earth3P-HR',
    this_var = 'siconc',
    this_variant_label = 'r1i1p2f1',
    this_modification = 'trim_QW_',
    select_summer = True,
    map_bbox = QW_BBOX,
    return_map = True,
)
display(this_map)
```
![EC-Earth3P-HR_r1i1p2f1_siconc_QW_JJASO_trend_map.png](investigate_specific_regions-img/EC-Earth3P-HR_r1i1p2f1_siconc_QW_JJASO_trend_map.png)

### Trimming data to QEI East
[back to top](#investigating-specific-regions)

#### Trimming EC-Earth3P-HR data to QEI East
[back to top](#investigating-specific-regions)

I can trim the data for `EC-Earth3P-HR` to the QEI East region.
This takes about 45 minutes to complete.
```python
import xarray as xr

from arctichoke.dataset import trim_files
from arctichoke.params import QE_BBOX
from arctichoke.path import list_variable_files

this_model = 'EC-Earth3P-HR'

for this_variant_label in [
    'r1i1p2f1', 
    'r2i1p2f1', 
    'r3i1p2f1',
]:
    for si_var in [
        'siconc',
        'sispeed',
        'sithick',
    ]:
        for this_experiment in ['hist-1950']:
            sivar_list = list_variable_files(
                source_id = this_model,
                variable_id = si_var,
                experiment_id = this_experiment,
                variant_label = this_variant_label,
            )
            trim_files(
                files_to_trim = sivar_list,
                name_prefix = 'trim_QE_',
                map_bbox = QE_BBOX,
                precise_trim = True,
            )
```
```
(trim_files) `name_prefix`: trim_QE_
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_QE_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_QE_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195101-195112.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/siconc/gn/v20181212/trim_QE_siconc_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195201-195212.nc`.
...
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/sithick/gn/v20190214/trim_QE_sithick_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201201-201212.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/sithick/gn/v20190214/trim_QE_sithick_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201301-201312.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/sithick/gn/v20190214/trim_QE_sithick_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201401-201412.nc`.
```

When trimming the marker variables, I specify `with_modification` to be `trim_CAA_` as I only calculated `sislow`, `sipacked`, and `silandfast` over the CAA.
This takes about 25 minutes. 
```python
import xarray as xr

from arctichoke.dataset import trim_files
from arctichoke.params import QE_BBOX
from arctichoke.path import list_variable_files

this_model = 'EC-Earth3P-HR'
this_experiment = 'hist-1950'
this_modification = 'trim_CAA_'

for this_variant_label in [
    'r1i1p2f1', 
    'r2i1p2f1', 
    'r3i1p2f1',
]:
    for si_var in [
        'sislow',
        'sipacked',
        'silandfast',
    ]:
        sivar_list = list_variable_files(
            source_id = this_model,
            variable_id = si_var,
            experiment_id = this_experiment,
            variant_label = this_variant_label,
            with_modification = this_modification,
        )
        trim_files(
            files_to_trim = sivar_list,
            name_prefix = 'trim_QE_',
            replace_prefix = this_modification,
            map_bbox = QE_BBOX,
            precise_trim = True,
        )
```
```
(trim_files) `name_prefix`: trim_QE_
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/sislow/gn/v20260617/trim_QE_sislow_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195001-195012.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/sislow/gn/v20260617/trim_QE_sislow_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195101-195112.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r1i1p2f1/SImon/sislow/gn/v20260617/trim_QE_sislow_SImon_EC-Earth3P-HR_hist-1950_r1i1p2f1_gn_195201-195212.nc`.
...
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/silandfast/gn/with_sispeed_clim/trim_QE_silandfast_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201201-201212.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/silandfast/gn/with_sispeed_clim/trim_QE_silandfast_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201301-201312.nc`.
	(trim_files) Writing file `/arctichoke_data/bergybits/data/CMIP6/HighResMIP/EC-Earth-Consortium/EC-Earth3P-HR/hist-1950/r3i1p2f1/SImon/silandfast/gn/with_sispeed_clim/trim_QE_silandfast_SImon_EC-Earth3P-HR_hist-1950_r3i1p2f1_gn_201401-201412.nc`.
```

I can use my `list_available_variables()` function to confirm how many trimmed files were created for each variable.
```python
from arctichoke.path import list_available_variables

list_available_variables(
    source_id = 'EC-Earth3P-HR',
    experiment_id = 'hist-1950',
    list_var_mods = True,
)
```
```
{'EC-Earth-Consortium/EC-Earth3P-HR': {'hist-1950': {'r1i1p2f1': {'SImon': {'siu': {'': 65},
     'siv': {'': 65},
     'sithick': {'': 455,
      'trim_CAA_': 65,
      'trim_NS_': 65,
      'trim_NWP_': 65,
      'trim_PC_': 65,
      'trim_QE_': 65,
      'trim_QW_': 65},
     'siage': {'': 65},
     'siconc': {'': 455,
      'trim_CAA_': 65,
      'trim_NS_': 65,
      'trim_NWP_': 65,
      'trim_PC_': 65,
      'trim_QE_': 65,
      'trim_QW_': 65},
     'sispeed': {'': 455,
      'trim_CAA_': 65,
      'trim_NS_': 65,
      'trim_NWP_': 65,
      'trim_PC_': 65,
      'trim_QE_': 65,
...
```

As a test, I can then use these trimmed data files to create a map of trends in a particular variable. 
I'll choose `siconc`.
```python
from arctichoke.params import QE_BBOX
from arctichoke.plot import make_trend_map 

this_map = make_trend_map(
    this_source_id = 'EC-Earth3P-HR',
    this_var = 'siconc',
    this_variant_label = 'r1i1p2f1',
    this_modification = 'trim_QE_',
    select_summer = True,
    map_bbox = QE_BBOX,
    return_map = True,
)
display(this_map)
```
![EC-Earth3P-HR_r1i1p2f1_siconc_QE_JJASO_trend_map.png](investigate_specific_regions-img/EC-Earth3P-HR_r1i1p2f1_siconc_QE_JJASO_trend_map.png)

---

## Finding spatial averages
[back to top](#investigating-specific-regions)

### Finding spatial averages of concentration
[back to top](#investigating-specific-regions)

My goal is to make a line plot of a time series to show how a particular variable changes within a specific region.
To do this, I will take the spatial average across a specific region for each time step.
First, I'll load the Nares Strait data for the first variant of `EC-Earth3P-HR` as an example.
```python
from arctichoke.path import list_variable_files

filelist = list_variable_files(
    source_id = 'EC-Earth3P-HR',
    variable_id = 'siconc',
    variant_label = 'r1i1p2f1',
    with_modification = 'trim_NS_',
    verbose = True,
)

import xarray as xr 

dataset = xr.open_mfdataset(filelist)
print(dataset) 
```
```console
(list_variable_files) Found 65 files.
/tmp/ipykernel_130/524186710.py:13: FutureWarning: In a future version of xarray the default value for data_vars will change from data_vars='all' to data_vars=None. This is likely to lead to different results when multiple datasets have matching variables with overlapping values. To opt in to new defaults and get rid of these warnings now use `set_options(use_new_combine_kwarg_defaults=True) or set data_vars explicitly.
  dataset = xr.open_mfdataset(filelist)
<xarray.Dataset> Size: 51MB
Dimensions:         (time: 780, bnds: 2, j: 41, i: 44, vertices: 4)
Coordinates:
  * time            (time) datetime64[ns] 6kB 1950-01-16T12:00:00 ... 2014-12...
  * j               (j) float64 328B 968.0 969.0 970.0 ... 1.007e+03 1.008e+03
  * i               (i) float64 352B 970.0 971.0 972.0 ... 1.012e+03 1.013e+03
    longitude       (j, i) float32 7kB dask.array<chunksize=(41, 44), meta=np.ndarray>
    latitude        (j, i) float32 7kB dask.array<chunksize=(41, 44), meta=np.ndarray>
Dimensions without coordinates: bnds, vertices
Data variables:
    time_bnds       (time, bnds) datetime64[ns] 12kB dask.array<chunksize=(1, 2), meta=np.ndarray>
    longitude_bnds  (time, j, i, vertices) float32 23MB dask.array<chunksize=(12, 41, 44, 4), meta=np.ndarray>
    latitude_bnds   (time, j, i, vertices) float32 23MB dask.array<chunksize=(12, 41, 44, 4), meta=np.ndarray>
    siconc          (time, j, i) float32 6MB dask.array<chunksize=(1, 41, 44), meta=np.ndarray>
Attributes: (12/48)
    CDI:                    Climate Data Interface version 2.5.1 (https://mpi...
    ...                     ...
    history:                Fri Aug 14 01:17:52 2026: cdo -O -s -f nc -sellon...
    CDO:                    Climate Data Operators version 2.5.1 (https://mpi...
```

Next, I'll use my `get_field_mean()` function which uses the `cdo.fldmean` command to calculate the spatially-weighted average of a variable.
```python
from arctichoke.dataset import get_field_mean

dataset_fldmean = get_field_mean(
    dataset,
    verbose = True,
)
print(dataset_fldmean)
```
```console
(get_field_mean) `save_as`: None
(get_field_mean) Dropping now-unnecessary dimensions: ('lat', 'lon')
<xarray.Dataset> Size: 22kB
Dimensions:    (time: 780, bnds: 2)
Coordinates:
  * time       (time) datetime64[ns] 6kB 1950-01-16T12:00:00 ... 2014-12-16T1...
Dimensions without coordinates: bnds
Data variables:
    time_bnds  (time, bnds) datetime64[ns] 12kB ...
    siconc     (time) float32 3kB ...
Attributes: (12/48)
    CDI:                    Climate Data Interface version 2.5.1 (https://mpi...
    ...                     ...
    history:                Mon Aug 17 15:19:14 2026: cdo -O -s -f nc -fldmea...
    CDO:                    Climate Data Operators version 2.5.1 (https://mpi...
```

The resulting dataset automatically drops the unnecessary latitude and longitude coordinates.

As a sanity check, I will plot the Nares Strait data for a few selected time slices and compare them to the spatial averages for the same time slices.
First, I'll plot January of 1950.
```python
from arctichoke.plot import quadmesh_map

quadmesh_map(
    dataset.sel(time='1950-01-16'),
    'siconc',
    map_bbox = NS_BBOX,
    clims = sps.sea_ice_vars['siconc']['plot_range'],
    add_region = False,
)
```
![EC-Earth3P-HR_r1i1p2f1_siconc_NS_1950-01_map_no_box.png](investigate_specific_regions-img/EC-Earth3P-HR_r1i1p2f1_siconc_NS_1950-01_map_no_box.png)

At this point in the model run, Nares Strait is almost completely ice covered.
I'll now see what the calculated spatial average is for this particular month.
```python
dataset_fldmean.sel(time='1950-01-16').compute()['siconc'].values
```
```console
array([96.435684], dtype=float32)
```

A spatial average of 96.44% seems reasonable given the map plotted above.

Now, I'll plot September of 2007, which was known to be a significant sea ice minimum.
```python
from arctichoke.plot import quadmesh_map

quadmesh_map(
    dataset.sel(time='2007-09-16'),
    'siconc',
    map_bbox = None,
)
```
![EC-Earth3P-HR_r1i1p2f1_siconc_NS_2007-09_map.png](investigate_specific_regions-img/EC-Earth3P-HR_r1i1p2f1_siconc_NS_2007-09_map.png)

Indeed, the map shows that Nares Strait was almost ice-free during this month.
There is a small region of high sea ice concentration on the Northern part of the strait, possibly representing an ice arch.
```python
dataset_fldmean.sel(time='2007-09-16').compute()['siconc'].values
```
```console
array([17.717651], dtype=float32)
```

The calculated spatial average of 17.72% seems reasonable given the map plotted above.

Next, I will perform a similar test over the QEI East region using `silandfast`.
```python
from arctichoke.path import list_variable_files

filelist = list_variable_files(
    source_id = 'EC-Earth3P-HR',
    variable_id = 'silandfast',
    variant_label = 'r1i1p2f1',
    with_modification = 'trim_QE_',
    version_id = 'v20260617',
    verbose = True,
)

import xarray as xr 

dataset = xr.open_mfdataset(filelist)
print(dataset)
```
```
(list_variable_files) Found 65 files.
/tmp/ipykernel_37/3422349004.py:14: FutureWarning: In a future version of xarray the default value for data_vars will change from data_vars='all' to data_vars=None. This is likely to lead to different results when multiple datasets have matching variables with overlapping values. To opt in to new defaults and get rid of these warnings now use `set_options(use_new_combine_kwarg_defaults=True) or set data_vars explicitly.
  dataset = xr.open_mfdataset(filelist)
<xarray.Dataset> Size: 123MB
Dimensions:         (time: 780, bnds: 2, j: 57, i: 77, vertices: 4)
Coordinates:
  * time            (time) datetime64[ns] 6kB 1950-01-16T12:00:00 ... 2014-12...
  * j               (j) float64 456B 974.0 975.0 976.0 ... 1.029e+03 1.03e+03
  * i               (i) float64 616B 920.0 921.0 922.0 ... 994.0 995.0 996.0
    longitude       (j, i) float32 18kB dask.array<chunksize=(57, 77), meta=np.ndarray>
    latitude        (j, i) float32 18kB dask.array<chunksize=(57, 77), meta=np.ndarray>
Dimensions without coordinates: bnds, vertices
Data variables:
    time_bnds       (time, bnds) datetime64[ns] 12kB dask.array<chunksize=(1, 2), meta=np.ndarray>
    longitude_bnds  (time, j, i, vertices) float32 55MB dask.array<chunksize=(12, 57, 77, 4), meta=np.ndarray>
    latitude_bnds   (time, j, i, vertices) float32 55MB dask.array<chunksize=(12, 57, 77, 4), meta=np.ndarray>
    silandfast      (time, j, i) float32 14MB dask.array<chunksize=(1, 57, 77), meta=np.ndarray>
Attributes: (12/48)
    CDI:                    Climate Data Interface version 2.5.1 (https://mpi...
    Conventions:            CF-1.7 CMIP-6.2
    source:                 EC-Earth3P-HR (2017): \naerosol: none\natmos: IFS...
    institution:            AEMET, Spain; BSC, Spain; CNR-ISAC, Italy; DMI, D...
    activity_id:            HighResMIP
    branch_method:          none provided
    ...                     ...
    physics_index:          2
    variant_label:          r1i1p2f1
    further_info_url:       https://furtherinfo.es-doc.org/CMIP6.EC-Earth-Con...
    contact:                cmip6-data@ec-earth.org
    history:                Tue Oct 13 18:25:49 2026: cdo -O -s -f nc -sellon...
    CDO:                    Climate Data Operators version 2.5.1 (https://mpi...
```

Next, I'll use my `get_field_mean()` function which uses the `cdo.fldmean` command to calculate the spatially-weighted average of a variable.
```python
from arctichoke.dataset import get_field_mean

dataset_fldmean = get_field_mean(
    dataset,
    verbose = True,
)
print(dataset_fldmean)
```
```
(get_field_mean) `save_as`: None
(get_field_mean) Dropping now-unnecessary dimensions: ('lat', 'lon')
<xarray.Dataset> Size: 22kB
Dimensions:     (time: 780, bnds: 2)
Coordinates:
  * time        (time) datetime64[ns] 6kB 1950-01-16T12:00:00 ... 2014-12-16T...
Dimensions without coordinates: bnds
Data variables:
    time_bnds   (time, bnds) datetime64[ns] 12kB ...
    silandfast  (time) float32 3kB ...
Attributes: (12/48)
    CDI:                    Climate Data Interface version 2.5.1 (https://mpi...
    Conventions:            CF-1.7 CMIP-6.2
    source:                 EC-Earth3P-HR (2017): \naerosol: none\natmos: IFS...
    institution:            AEMET, Spain; BSC, Spain; CNR-ISAC, Italy; DMI, D...
    activity_id:            HighResMIP
    branch_method:          none provided
    ...                     ...
    physics_index:          2
    variant_label:          r1i1p2f1
    further_info_url:       https://furtherinfo.es-doc.org/CMIP6.EC-Earth-Con...
    contact:                cmip6-data@ec-earth.org
    history:                Tue Oct 13 19:20:16 2026: cdo -O -s -f nc -fldmea...
    CDO:                    Climate Data Operators version 2.5.1 (https://mpi...
```

As a sanity check, I will plot the QEI East data for a few selected time slices and compare them to the spatial averages for the same time slices.
First, I'll plot June of 1950.
```python
from arctichoke.plot import quadmesh_map

quadmesh_map(
    dataset.sel(time='1950-06-16'),
    'silandfast',
    map_bbox = sps.QE_BBOX,
    clims = sps.sea_ice_vars['silandfast']['plot_range'],
    add_region = False,
)
```
![EC-Earth3P-HR_r1i1p2f1_silandfast_QE_1950-06_map.png](investigate_specific_regions-img/EC-Earth3P-HR_r1i1p2f1_silandfast_QE_1950-06_map.png)

At this point in the model run, QEI East is almost completely ice covered. I'll now see what the calculated spatial average is for this particular month.
```python
dataset_fldmean.sel(time='1950-06-16').compute()['silandfast'].values
```
```
array([0.788712], dtype=float32)
```

That seems to match pretty well. 

Next, I'll take a look at `silandfast` in the QEI East in September of 2007.
```python
from arctichoke.plot import quadmesh_map

quadmesh_map(
    dataset.sel(time='2007-09-16'),
    'silandfast',
    map_bbox = sps.QE_BBOX,
    clims = sps.sea_ice_vars['silandfast']['plot_range'],
    add_region = False,
)
```
![EC-Earth3P-HR_r1i1p2f1_silandfast_QE_2007-09_map.png](investigate_specific_regions-img/EC-Earth3P-HR_r1i1p2f1_silandfast_QE_2007-09_map.png)

```python
dataset_fldmean.sel(time='2007-09-16').compute()['silandfast'].values
```
```
array([0.3039074], dtype=float32)
```

Again, the calculated value matches what I would expect from the plot.


### Finding spatial averages of concentration where thickness is > 2 m
[back to top](#investigating-specific-regions)

In addition to regular variables like `siconc`, I would like to be able to find spatial averages of sea ice concentration, but filtered to only where sea ice thickness (`sithick`) is greater than 2 meters.
To do so, I added the argument `sum_by` to the `make_sithick_masked_climatology()` function introduced in {doc}`Making sea ice climatologies <../docs_analysis/climatologies>`.
This means I can choose between using `sum_by_month()`, which is the default, and `sum_by_year()`, which is what I need for this particular scenario.
I also make sure to specify `start_year` and `end_year` to cover the entire time period as well as setting `select_summer` to `True`.
This gives me a dataset which has one value per year for each grid cell in the specific region.
I'll take Nares Strait as an example.
```python
from arctichoke.analysis import make_sithick_masked_climatology

dataset_m_clim = make_sithick_masked_climatology(
    this_source_id = 'EC-Earth3P-HR',
    this_var = 'siconc',
    this_variant_label = 'r1i1p2f1',
    this_modification = 'trim_NS_',
    start_year = 1950,
    end_year = 2014,
    sum_by = 'year',
    select_summer = True,
    verbose = False,
)
print(dataset_m_clim)
```
```console
<xarray.Dataset> Size: 485kB
Dimensions:                     (year: 65, j: 41, i: 44)
Coordinates:
  * year                        (year) int64 520B 1950 1951 1952 ... 2013 2014
  * j                           (j) float64 328B 968.0 969.0 ... 1.008e+03
  * i                           (i) float64 352B 970.0 971.0 ... 1.013e+03
    longitude                   (j, i) float32 7kB dask.array<chunksize=(41, 44), meta=np.ndarray>
    latitude                    (j, i) float32 7kB dask.array<chunksize=(41, 44), meta=np.ndarray>
Data variables:
    siconc_si2mthick_year_mean  (year, j, i) float32 469kB dask.array<chunksize=(1, 41, 44), meta=np.ndarray>
Attributes: (12/49)
    CDI:                    Climate Data Interface version 2.5.1 (https://mpi...
    Conventions:            CF-1.7 CMIP-6.2
    source:                 EC-Earth3P-HR (2017): \naerosol: none\natmos: IFS...
    institution:            AEMET, Spain; BSC, Spain; CNR-ISAC, Italy; DMI, D...
    activity_id:            HighResMIP
    ...                     ...
    variant_label:          r1i1p2f1
    history:                2026-08-27T17:15:19Z altered by `arctichoke`: Cal...
    CDO:                    Climate Data Operators version 2.5.1 (https://mpi...
    select_months:          [6, 7, 8, 9, 10]
```

From here, I can then get the spatial average and then plot the time series.
```python
from arctichoke.dataset import get_field_mean

dataset_m_fldmean = get_field_mean(
    dataset_m_clim,
)

from arctichoke.plot import plot_time_series 

plot_time_series(
    dataset_m_fldmean,
    'siconc_si2mthick_year_mean',
    add_regression = True,
)
```
```console
(plot_time_series) Slope of `siconc_si2mthick_year_mean` regression line: -2.32762e-01
```
![EC-Earth3P-HR_r1i1p2f1_siconc_NS_JJASO_fldmean_si2mthick_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_r1i1p2f1_siconc_NS_JJASO_fldmean_si2mthick_trend.png)

I then wrote this functionality, along with plotting time series that aren't filtered by sea ice thickness, into the function `plot_multi_time_series()` which I will make use of in the next section.

---

## Time series plots for specific regions
[back to top](#investigating-specific-regions)

Now, I am ready to make the time series plots that I plan on including in my study.
I will make a time series for each variable separately, but plot both the yearly values and the trends for the three realizations (variant labels) on the same axis.

### Time series plots for Nares Strait
[back to top](#investigating-specific-regions)

#### Nares Strait time series for EC-Earth3P-HR
[back to top](#investigating-specific-regions)

First, I'll make time series plots for Nares Strait.
In between each variable, I need to call `plt.show()` to have the plot show up, then `plt.clf()` to clear the figure so that the lines for the next variable aren't plotted onto the same axis as those of the previous variable.
```python
import matplotlib.pyplot as plt 

from arctichoke.plot import plot_multi_time_series

this_model = 'EC-Earth3P-HR'
this_modification = 'trim_NS_'
set_verbose = False

for variable_id in [
    'sispeed',
    'siconc',
    'sislow',
    'sipacked',
]:
    plot_multi_time_series(
        this_source_id = this_model,
        this_var = variable_id,
        this_modification = this_modification,
        verbose = set_verbose,
    )
    # Need to show, then clear the figure so they aren't plotted on top of one another
    plt.show()
    plt.clf()
    if variable_id == 'siconc':
        plot_multi_time_series(
            this_source_id = this_model,
            this_var = variable_id,
            this_modification = this_modification,
            mask_by_sithick = True,
            verbose = set_verbose,
        )
        plt.show()
        plt.clf()

for variable_id in [
    'silandfast',
]:
    for this_version_id in [
        'v20260617',
        'with_sispeed_clim',
        'with_siconc_clim',
    ]:
        plot_multi_time_series(
            this_source_id = this_model,
            this_var = variable_id,
            this_modification = this_modification,
            this_version_id = this_version_id,
            verbose = set_verbose,
        )
        # Need to show, then clear the figure so they aren't plotted on top of one another
        plt.show()
        plt.clf()
```
<!-- ![EC-Earth3P-HR_all_variants_sithick_NS_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_sithick_NS_JJASO_fldmean_trend.png) -->
```console
(plot_time_series) Slope of `sispeed_year_mean` regression line:  3.57291e-04
(plot_time_series) Slope of `sispeed_year_mean` regression line: -5.49426e-05
(plot_time_series) Slope of `sispeed_year_mean` regression line:  9.62230e-04
```
![EC-Earth3P-HR_all_variants_sispeed_NS_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_sispeed_NS_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `siconc_year_mean` regression line: -2.16005e-01
(plot_time_series) Slope of `siconc_year_mean` regression line:  6.98471e-02
(plot_time_series) Slope of `siconc_year_mean` regression line: -6.19737e-01
```
![EC-Earth3P-HR_all_variants_siconc_NS_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_siconc_NS_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `siconc_si2mthick_year_mean` regression line: -2.32762e-01
(plot_time_series) Slope of `siconc_si2mthick_year_mean` regression line:  1.14792e-01
(plot_time_series) Slope of `siconc_si2mthick_year_mean` regression line: -6.62753e-01
```
![EC-Earth3P-HR_all_variants_siconc_NS_JJASO_fldmean_si2mthick_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_siconc_NS_JJASO_fldmean_si2mthick_trend.png)
```console
(plot_time_series) Slope of `sislow_year_sum` regression line: -1.15160e-02
(plot_time_series) Slope of `sislow_year_sum` regression line:  3.38715e-03
(plot_time_series) Slope of `sislow_year_sum` regression line: -4.31424e-02
```
![EC-Earth3P-HR_all_variants_sislow_NS_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_sislow_NS_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `sipacked_year_sum` regression line: -1.41143e-02
(plot_time_series) Slope of `sipacked_year_sum` regression line:  3.20485e-03
(plot_time_series) Slope of `sipacked_year_sum` regression line: -4.28847e-02
```
![EC-Earth3P-HR_all_variants_sipacked_NS_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_sipacked_NS_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.24325e-02
(plot_time_series) Slope of `silandfast_year_sum` regression line:  3.39746e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -4.39438e-02
```
![EC-Earth3P-HR_all_variants_silandfast_NS_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_silandfast_NS_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.39328e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.74543e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -7.49006e-03
```
![EC-Earth3P-HR_all_variants_silandfast_NS_JJASO_fldmean_slow_clim_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_silandfast_NS_JJASO_fldmean_slow_clim_trend.png)
```console
(plot_time_series) Slope of `silandfast_year_sum` regression line: -4.86336e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line:  8.22941e-04
(plot_time_series) Slope of `silandfast_year_sum` regression line: -2.04846e-02
```
![EC-Earth3P-HR_all_variants_silandfast_NS_JJASO_fldmean_packed_clim_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_silandfast_NS_JJASO_fldmean_packed_clim_trend.png)

#### Nares Strait time series for HadGEM3-GC31-MM
[back to top](#investigating-specific-regions)

Here is the same series of plots as above, but for `HadGEM3-GC31-MM`.
```python
import matplotlib.pyplot as plt 

from arctichoke.plot import plot_multi_time_series

this_model = 'HadGEM3-GC31-MM'
this_modification = 'trim_NS_'
set_verbose = False

for variable_id in [
    'sispeed',
    'siconc2',
    # 'sislow',
    # 'sipacked',
]:
    plot_multi_time_series(
        this_source_id = this_model,
        this_var = variable_id,
        this_modification = this_modification,
        verbose = set_verbose,
    )
    # Need to show, then clear the figure so they aren't plotted on top of one another
    plt.show()
    plt.clf()
    if variable_id == 'siconc2':
        plot_multi_time_series(
            this_source_id = this_model,
            this_var = variable_id,
            this_modification = this_modification,
            mask_by_sithick = True,
            verbose = set_verbose,
        )
        plt.show()
        plt.clf()

for variable_id in [
    'silandfast',
]:
    for this_version_id in [
        'v20260617',
        'with_sispeed_clim',
        'with_siconc_clim',
    ]:
        plot_multi_time_series(
            this_source_id = this_model,
            this_var = variable_id,
            this_modification = this_modification,
            this_version_id = this_version_id,
            verbose = set_verbose,
        )
        # Need to show, then clear the figure so they aren't plotted on top of one another
        plt.show()
        plt.clf()
```
```
(plot_time_series) Slope of `sispeed_year_mean` regression line:  2.68859e-04
(plot_time_series) Slope of `sispeed_year_mean` regression line:  2.82197e-04
(plot_time_series) Slope of `sispeed_year_mean` regression line:  4.44678e-04
```
![HadGEM3-GC31-MM_all_variants_sispeed_NS_JJASO_fldmean_trend.png](investigate_specific_regions-img/HadGEM3-GC31-MM_all_variants_sispeed_NS_JJASO_fldmean_trend.png)

```
(plot_time_series) Slope of `siconc2_year_mean` regression line: -1.30954e-01
(plot_time_series) Slope of `siconc2_year_mean` regression line: -1.63957e-02
(plot_time_series) Slope of `siconc2_year_mean` regression line:  6.37614e-03
```
![HadGEM3-GC31-MM_all_variants_siconc2_NS_JJASO_fldmean_trend.png](investigate_specific_regions-img/HadGEM3-GC31-MM_all_variants_siconc2_NS_JJASO_fldmean_trend.png)

```
(plot_time_series) Slope of `siconc2_si2mthick_year_mean` regression line: -2.20039e-01
(plot_time_series) Slope of `siconc2_si2mthick_year_mean` regression line: -4.41596e-02
(plot_time_series) Slope of `siconc2_si2mthick_year_mean` regression line: -5.48348e-04
```
![HadGEM3-GC31-MM_all_variants_siconc2_si2mthick_NS_JJASO_fldmean_trend.png](investigate_specific_regions-img/HadGEM3-GC31-MM_all_variants_siconc2_si2mthick_NS_JJASO_fldmean_trend.png)

```
(plot_time_series) Slope of `silandfast_year_sum` regression line: -3.68894e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.64123e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -3.29077e-03
```
![HadGEM3-GC31-MM_all_variants_silandfast_NS_JJASO_fldmean_trend.png](investigate_specific_regions-img/HadGEM3-GC31-MM_all_variants_silandfast_NS_JJASO_fldmean_trend.png)

```
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.86724e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -6.01252e-04
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.53820e-03
```
![HadGEM3-GC31-MM_all_variants_silandfast_NS_JJASO_sislow_clim_fldmean_trend.png](investigate_specific_regions-img/HadGEM3-GC31-MM_all_variants_silandfast_NS_JJASO_sislow_clim_fldmean_trend.png)

```
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.50460e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -8.62236e-04
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.25308e-03
```
![HadGEM3-GC31-MM_all_variants_silandfast_NS_JJASO_sipacked_clim_fldmean_trend.png](investigate_specific_regions-img/HadGEM3-GC31-MM_all_variants_silandfast_NS_JJASO_sipacked_clim_fldmean_trend.png)


### Time series plots for Parry Channel
[back to top](#investigating-specific-regions)

#### Parry Channel time series for EC-Earth3P-HR
[back to top](#investigating-specific-regions)

Next, I'll make time series plots for Parry Channel.
Again, between each variable, I need to call `plt.show()` then `plt.clf()` to avoid all variables being plotted on the same axis.
```python
import matplotlib.pyplot as plt 

from arctichoke.plot import plot_multi_time_series

this_model = 'EC-Earth3P-HR'
this_modification = 'trim_PC_'
set_verbose = False

for variable_id in [
    'sispeed',
    'siconc',
    'sislow',
    'sipacked',
]:
    plot_multi_time_series(
        this_source_id = this_model,
        this_var = variable_id,
        this_modification = this_modification,
        verbose = set_verbose,
    )
    # Need to show, then clear the figure so they aren't plotted on top of one another
    plt.show()
    plt.clf()
    if variable_id == 'siconc':
        plot_multi_time_series(
            this_source_id = this_model,
            this_var = variable_id,
            this_modification = this_modification,
            mask_by_sithick = True,
            verbose = set_verbose,
        )
        plt.show()
        plt.clf()

for variable_id in [
    'silandfast',
]:
    for this_version_id in [
        'v20260617',
        'with_sispeed_clim',
        'with_siconc_clim',
    ]:
        plot_multi_time_series(
            this_source_id = this_model,
            this_var = variable_id,
            this_modification = this_modification,
            this_version_id = this_version_id,
            verbose = set_verbose,
        )
        # Need to show, then clear the figure so they aren't plotted on top of one another
        plt.show()
        plt.clf()
```
<!-- ![EC-Earth3P-HR_all_variants_sithick_PC_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_sithick_PC_JJASO_fldmean_trend.png) -->
```console
(plot_time_series) Slope of `sispeed_year_mean` regression line:  3.14328e-04
(plot_time_series) Slope of `sispeed_year_mean` regression line:  5.99957e-04
(plot_time_series) Slope of `sispeed_year_mean` regression line:  7.21741e-04
```
![EC-Earth3P-HR_all_variants_sispeed_PC_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_sispeed_PC_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `siconc_year_mean` regression line: -1.62090e-01
(plot_time_series) Slope of `siconc_year_mean` regression line: -2.96469e-01
(plot_time_series) Slope of `siconc_year_mean` regression line: -4.59905e-01
```
![EC-Earth3P-HR_all_variants_siconc_PC_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_siconc_PC_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `siconc_si2mthick_year_mean` regression line: -1.85276e-01
(plot_time_series) Slope of `siconc_si2mthick_year_mean` regression line: -3.22107e-01
(plot_time_series) Slope of `siconc_si2mthick_year_mean` regression line: -4.68885e-01
```
![EC-Earth3P-HR_all_variants_siconc_PC_JJASO_fldmean_si2mthick_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_siconc_PC_JJASO_fldmean_si2mthick_trend.png)
```console
(plot_time_series) Slope of `sislow_year_sum` regression line: -5.82038e-03
(plot_time_series) Slope of `sislow_year_sum` regression line: -1.59661e-02
(plot_time_series) Slope of `sislow_year_sum` regression line: -1.58646e-02
```
![EC-Earth3P-HR_all_variants_sislow_PC_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_sislow_PC_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `sipacked_year_sum` regression line: -1.32887e-02
(plot_time_series) Slope of `sipacked_year_sum` regression line: -2.48616e-02
(plot_time_series) Slope of `sipacked_year_sum` regression line: -3.18017e-02
```
![EC-Earth3P-HR_all_variants_sipacked_PC_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_sipacked_PC_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `silandfast_year_sum` regression line: -6.36820e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.63635e-02
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.74537e-02
```
![EC-Earth3P-HR_all_variants_silandfast_PC_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_silandfast_PC_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `silandfast_year_sum` regression line: -2.43093e-04
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.32291e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -2.14862e-03
```
![EC-Earth3P-HR_all_variants_silandfast_PC_JJASO_fldmean_slow_clim_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_silandfast_PC_JJASO_fldmean_slow_clim_trend.png)
```console
(plot_time_series) Slope of `silandfast_year_sum` regression line: -5.76872e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.51612e-02
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.60920e-02
```
![EC-Earth3P-HR_all_variants_silandfast_PC_JJASO_fldmean_packed_clim_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_silandfast_PC_JJASO_fldmean_packed_clim_trend.png)

#### Parry Channel time series for HadGEM3-GC31-MM
[back to top](#investigating-specific-regions)

This shows the same plots as above for Parry Channel, but using data from `HadGEM3-GC31-MM`.
```python
import matplotlib.pyplot as plt 

from arctichoke.plot import plot_multi_time_series

this_model = 'HadGEM3-GC31-MM'
this_modification = 'trim_PC_'
set_verbose = False

for variable_id in [
    'sispeed',
    'siconc2',
    # 'sislow',
    # 'sipacked',
]:
    plot_multi_time_series(
        this_source_id = this_model,
        this_var = variable_id,
        this_modification = this_modification,
        verbose = set_verbose,
    )
    # Need to show, then clear the figure so they aren't plotted on top of one another
    plt.show()
    plt.clf()
    if variable_id == 'siconc2':
        plot_multi_time_series(
            this_source_id = this_model,
            this_var = variable_id,
            this_modification = this_modification,
            mask_by_sithick = True,
            verbose = set_verbose,
        )
        plt.show()
        plt.clf()

for variable_id in [
    'silandfast',
]:
    for this_version_id in [
        'v20260617',
        'with_sispeed_clim',
        'with_siconc_clim',
    ]:
        plot_multi_time_series(
            this_source_id = this_model,
            this_var = variable_id,
            this_modification = this_modification,
            this_version_id = this_version_id,
            verbose = set_verbose,
        )
        # Need to show, then clear the figure so they aren't plotted on top of one another
        plt.show()
        plt.clf()
```
```
(plot_time_series) Slope of `sispeed_year_mean` regression line:  4.94116e-04
(plot_time_series) Slope of `sispeed_year_mean` regression line:  1.97457e-04
(plot_time_series) Slope of `sispeed_year_mean` regression line:  1.16132e-04
```
![HadGEM3-GC31-MM_all_variants_sispeed_PC_JJASO_fldmean_trend.png](investigate_specific_regions-img/HadGEM3-GC31-MM_all_variants_sispeed_PC_JJASO_fldmean_trend.png)

```
(plot_time_series) Slope of `siconc2_year_mean` regression line: -2.62304e-01
(plot_time_series) Slope of `siconc2_year_mean` regression line: -8.66367e-02
(plot_time_series) Slope of `siconc2_year_mean` regression line: -9.80721e-02
```
![HadGEM3-GC31-MM_all_variants_siconc2_PC_JJASO_fldmean_trend.png](investigate_specific_regions-img/HadGEM3-GC31-MM_all_variants_siconc2_PC_JJASO_fldmean_trend.png)

```
(plot_time_series) Slope of `siconc2_si2mthick_year_mean` regression line: -2.79901e-01
(plot_time_series) Slope of `siconc2_si2mthick_year_mean` regression line: -8.29012e-02
(plot_time_series) Slope of `siconc2_si2mthick_year_mean` regression line: -7.40043e-02
```
![HadGEM3-GC31-MM_all_variants_siconc2_si2mthick_PC_JJASO_fldmean_trend.png](investigate_specific_regions-img/HadGEM3-GC31-MM_all_variants_siconc2_si2mthick_PC_JJASO_fldmean_trend.png)

```
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.12843e-02
(plot_time_series) Slope of `silandfast_year_sum` regression line: -2.91749e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -2.60937e-03
```
![HadGEM3-GC31-MM_all_variants_silandfast_PC_JJASO_fldmean_trend.png](investigate_specific_regions-img/HadGEM3-GC31-MM_all_variants_silandfast_PC_JJASO_fldmean_trend.png)

```
(plot_time_series) Slope of `silandfast_year_sum` regression line: -2.35436e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -4.30923e-04
(plot_time_series) Slope of `silandfast_year_sum` regression line: -6.63102e-04
```
![HadGEM3-GC31-MM_all_variants_silandfast_PC_JJASO_sislow_clim_fldmean_trend.png](investigate_specific_regions-img/HadGEM3-GC31-MM_all_variants_silandfast_PC_JJASO_sislow_clim_fldmean_trend.png)

```
(plot_time_series) Slope of `silandfast_year_sum` regression line: -9.75152e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -2.71984e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -2.09174e-03
```
![HadGEM3-GC31-MM_all_variants_silandfast_PC_JJASO_sipacked_clim_fldmean_trend.png](investigate_specific_regions-img/HadGEM3-GC31-MM_all_variants_silandfast_PC_JJASO_sipacked_clim_fldmean_trend.png)

### Time series plots for QEI West
[back to top](#investigating-specific-regions)

#### QEI West time series for EC-Earth3P-HR
[back to top](#investigating-specific-regions)

Next, I'll make time series plots for QEI West.
Again, between each variable, I need to call `plt.show()` then `plt.clf()` to avoid all variables being plotted on the same axis.
```python
import matplotlib.pyplot as plt 

from arctichoke.plot import plot_multi_time_series

this_model = 'EC-Earth3P-HR'
this_modification = 'trim_QW_'
set_verbose = False

for variable_id in [
    'sispeed',
    'siconc',
    'sislow',
    'sipacked',
]:
    plot_multi_time_series(
        this_source_id = this_model,
        this_var = variable_id,
        this_modification = this_modification,
        verbose = set_verbose,
    )
    # Need to show, then clear the figure so they aren't plotted on top of one another
    plt.show()
    plt.clf()
    if variable_id == 'siconc':
        plot_multi_time_series(
            this_source_id = this_model,
            this_var = variable_id,
            this_modification = this_modification,
            mask_by_sithick = True,
            verbose = set_verbose,
        )
        plt.show()
        plt.clf()

for variable_id in [
    'silandfast',
]:
    for this_version_id in [
        'v20260617',
        'with_sispeed_clim',
        'with_siconc_clim',
    ]:
        plot_multi_time_series(
            this_source_id = this_model,
            this_var = variable_id,
            this_modification = this_modification,
            this_version_id = this_version_id,
            verbose = set_verbose,
        )
        # Need to show, then clear the figure so they aren't plotted on top of one another
        plt.show()
        plt.clf()
```
```console
(plot_time_series) Slope of `sispeed_year_mean` regression line:  2.40936e-04
(plot_time_series) Slope of `sispeed_year_mean` regression line:  4.04943e-04
(plot_time_series) Slope of `sispeed_year_mean` regression line:  4.24609e-04
```
![EC-Earth3P-HR_all_variants_sispeed_QW_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_sispeed_QW_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `siconc_year_mean` regression line: -6.53495e-02
(plot_time_series) Slope of `siconc_year_mean` regression line: -1.10695e-01
(plot_time_series) Slope of `siconc_year_mean` regression line: -1.35667e-01
```
![EC-Earth3P-HR_all_variants_siconc_QW_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_siconc_QW_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `siconc_si2mthick_year_mean` regression line: -7.49443e-02
(plot_time_series) Slope of `siconc_si2mthick_year_mean` regression line: -1.21773e-01
(plot_time_series) Slope of `siconc_si2mthick_year_mean` regression line: -1.48875e-01
```
![EC-Earth3P-HR_all_variants_siconc_QW_JJASO_fldmean_si2mthick_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_siconc_QW_JJASO_fldmean_si2mthick_trend.png)
```console
(plot_time_series) Slope of `sislow_year_sum` regression line: -1.48770e-02
(plot_time_series) Slope of `sislow_year_sum` regression line: -2.48677e-02
(plot_time_series) Slope of `sislow_year_sum` regression line: -2.06977e-02
```
![EC-Earth3P-HR_all_variants_sislow_QW_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_sislow_QW_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `sipacked_year_sum` regression line: -8.11810e-03
(plot_time_series) Slope of `sipacked_year_sum` regression line: -1.57263e-02
(plot_time_series) Slope of `sipacked_year_sum` regression line: -1.69076e-02
```
![EC-Earth3P-HR_all_variants_sipacked_QW_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_sipacked_QW_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.46268e-02
(plot_time_series) Slope of `silandfast_year_sum` regression line: -2.46585e-02
(plot_time_series) Slope of `silandfast_year_sum` regression line: -2.06017e-02
```
![EC-Earth3P-HR_all_variants_silandfast_QW_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_silandfast_QW_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.88192e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -5.47205e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -5.30801e-03
```
![EC-Earth3P-HR_all_variants_silandfast_QW_JJASO_fldmean_slow_clim_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_silandfast_QW_JJASO_fldmean_slow_clim_trend.png)
```console
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.28967e-02
(plot_time_series) Slope of `silandfast_year_sum` regression line: -2.25835e-02
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.79259e-02
```
![EC-Earth3P-HR_all_variants_silandfast_QW_JJASO_fldmean_packed_clim_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_silandfast_QW_JJASO_fldmean_packed_clim_trend.png)

### Time series plots for QEI East
[back to top](#investigating-specific-regions)

#### QEI East time series for EC-Earth3P-HR
[back to top](#investigating-specific-regions)

Next, I'll make time series plots for QEI East.
Again, between each variable, I need to call `plt.show()` then `plt.clf()` to avoid all variables being plotted on the same axis.
```python
import matplotlib.pyplot as plt 

from arctichoke.plot import plot_multi_time_series

this_model = 'EC-Earth3P-HR'
this_modification = 'trim_QE_'
set_verbose = False

for variable_id in [
    'sispeed',
    'siconc',
    'sislow',
    'sipacked',
]:
    plot_multi_time_series(
        this_source_id = this_model,
        this_var = variable_id,
        this_modification = this_modification,
        verbose = set_verbose,
    )
    # Need to show, then clear the figure so they aren't plotted on top of one another
    plt.show()
    plt.clf()
    if variable_id == 'siconc':
        plot_multi_time_series(
            this_source_id = this_model,
            this_var = variable_id,
            this_modification = this_modification,
            mask_by_sithick = True,
            verbose = set_verbose,
        )
        plt.show()
        plt.clf()

for variable_id in [
    'silandfast',
]:
    for this_version_id in [
        'v20260617',
        'with_sispeed_clim',
        'with_siconc_clim',
    ]:
        plot_multi_time_series(
            this_source_id = this_model,
            this_var = variable_id,
            this_modification = this_modification,
            this_version_id = this_version_id,
            verbose = set_verbose,
        )
        # Need to show, then clear the figure so they aren't plotted on top of one another
        plt.show()
        plt.clf()
```
```console
(plot_time_series) Slope of `sispeed_year_mean` regression line:  1.97656e-04
(plot_time_series) Slope of `sispeed_year_mean` regression line:  1.77828e-04
(plot_time_series) Slope of `sispeed_year_mean` regression line:  2.09376e-04
```
![EC-Earth3P-HR_all_variants_sispeed_QW_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_sispeed_QW_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `siconc_year_mean` regression line: -1.30965e-01
(plot_time_series) Slope of `siconc_year_mean` regression line: -1.33934e-01
(plot_time_series) Slope of `siconc_year_mean` regression line: -1.99849e-01
```
![EC-Earth3P-HR_all_variants_siconc_QW_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_siconc_QW_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `siconc_si2mthick_year_mean` regression line: -1.50413e-01
(plot_time_series) Slope of `siconc_si2mthick_year_mean` regression line: -1.51599e-01
(plot_time_series) Slope of `siconc_si2mthick_year_mean` regression line: -1.93461e-01
```
![EC-Earth3P-HR_all_variants_siconc_QW_JJASO_fldmean_si2mthick_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_siconc_QW_JJASO_fldmean_si2mthick_trend.png)
```console
(plot_time_series) Slope of `sislow_year_sum` regression line: -1.00557e-02
(plot_time_series) Slope of `sislow_year_sum` regression line: -9.02848e-03
(plot_time_series) Slope of `sislow_year_sum` regression line: -1.08237e-02
```
![EC-Earth3P-HR_all_variants_sislow_QW_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_sislow_QW_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `sipacked_year_sum` regression line: -1.00129e-02
(plot_time_series) Slope of `sipacked_year_sum` regression line: -9.95049e-03
(plot_time_series) Slope of `sipacked_year_sum` regression line: -1.35190e-02
```
![EC-Earth3P-HR_all_variants_sipacked_QW_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_sipacked_QW_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.06822e-02
(plot_time_series) Slope of `silandfast_year_sum` regression line: -9.56890e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -1.17402e-02
```
![EC-Earth3P-HR_all_variants_silandfast_QW_JJASO_fldmean_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_silandfast_QW_JJASO_fldmean_trend.png)
```console
(plot_time_series) Slope of `silandfast_year_sum` regression line: -3.93401e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -4.56013e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -3.94723e-03
```
![EC-Earth3P-HR_all_variants_silandfast_QW_JJASO_fldmean_slow_clim_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_silandfast_QW_JJASO_fldmean_slow_clim_trend.png)
```console
(plot_time_series) Slope of `silandfast_year_sum` regression line: -7.95024e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -7.56321e-03
(plot_time_series) Slope of `silandfast_year_sum` regression line: -7.55018e-03
```
![EC-Earth3P-HR_all_variants_silandfast_QW_JJASO_fldmean_packed_clim_trend.png](investigate_specific_regions-img/EC-Earth3P-HR_all_variants_silandfast_QW_JJASO_fldmean_packed_clim_trend.png)
