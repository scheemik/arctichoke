<a id='top'></a>
# Downloading model data with `esgpull`

The instructions below show how to use `esgpull` within the container to download CMIP6 HighResMIP model data.
For more details on how the architecture of this project was developed, see the {doc}`Initial Setup <../data_setup/initial_setup>` guide. 

## Contents

- [Why `esgpull`?](#esgpull_why)
- [Searching for data](#esgpull_search)
    - [Search filtering](#esgpull_search_filter)
- [Add, track, and update queries](#esgpull_queries)
- [Downloading data](#esgpull_download)
    - [Retrying failed downloads](#esgpull_download_retry)

---
<a id='esgpull_why'></a>
[back to top](#top)

## Why `esgpull`?

Data from the CMIP6 HighResMIP models are available to download from the [ESGF Federated Nodes](https://esgf-node.ornl.gov/search) webportal.
The search functionality on that site is excellent, making it easy to see what data is available across the federated nodes.
Upon finding the data yuo want, you can click to download an individual file.
This is useful when exploring what a model's data look like, especially when only concerned with fixed variables, that is, variables that don't change over time (like `areacello`, the area of each grid cell that is ocean).

However, things become unmanagable very quickly when trying to download hundreds of individual files. 
For example, the `hist-1950` experiment runs from 1950 to 2015, covering 65 years. 
Many variables are output on a monthly basis, and grouped into yearly files. 
Each of these files can be between 20 to 200 MB depending on the model. 
If you need data for many different variables and / or many different models, this can add up quickly.

$$ \text{Disk space used} = \text{Years covered} \times \text{Number of variables} \times \text{Number of models} \times \text{20-200 MB} $$

I have no desire to try and manage that amount of data manually.

The webportal does advertize the functionality to generate a `wget` script from a filtered search, however I have not been able to actually get that to work.
There is a way to augment the webportal with [Globus Connect Personal](https://www.globus.org/globus-connect-personal) which handles downloading many files for you. 
I documented how I was able to get that to work in the {doc}`Downloading model data with Globus <globus_downloads>` guide. 
However, it involves a bunch of mouse clicks to navigate many pages of a GUI and the downloads all go into one folder in a flat structure.

I decided to use [`esgpull`](https://esgf.github.io/esgf-download/quickstart/) for this project as it offers a way to programmatically download data from HighResMIP models. 
This means, I can write a script that downloads exactly the data I want and can assume that the data will be in a predictable, and expandable, directory structure, making it much more straight-forward to write functions that interact with model data that can apply to new model data as it is downloaded.
To get an idea of what the file structure created by `esgpull` looks like, below is a truncated example.

```{include} data_dir_structure.md
```

---
<a id='esgpull_search'></a>
[back to top](#top)

## Searching for data

The `esgpull` documentation page for [Data discovery](https://esgf.github.io/esgf-download/search/#free-text-search) gives examples of how to perform searches.
Basically, it amounts to running the `esgpull search` command followed by arguments to filter the results.

Without any filters, the search returns a very large number of results.
```console
(seaicecp) root@<container_id>:/workspace# uv run esgpull search
Found 14427436 datasets.
 id │                               dataset                               │ #  │   size    
════╪═════════════════════════════════════════════════════════════════════╪════╪═══════════
  0 │ cmip5.output.CCCma.CanCM4.decadal1967.mon.land.r7i1p1.v20130331     │ 11 │  56.4 MiB 
  1 │ cmip5.output.CCCma.CanCM4.decadal1967.mon.landIce.r5i1p1.v20130331  │  6 │  22.6 MiB 
  2 │ cmip5.output.CCCma.CanCM4.decadal1982.mon.landIce.r2i1p1.v20130331  │  6 │  22.6 MiB 
  3 │ cmip5.output.CCCma.CanCM4.decadal1982.mon.landIce.r7i1p1.v20130331  │  6 │  22.6 MiB 
  4 │ cmip5.output.CCCma.CanCM4.decadal1982.mon.ocean.r5i1p1.v20130331    │ 32 │   6.6 GiB 
  5 │ cmip5.output.CCCma.CanCM4.decadal1983.day.atmos.r4i1p1.v20130331    │ 23 │   2.6 GiB 
  6 │ cmip5.output.CCCma.CanCM4.decadal1983.day.landIce.r8i1p1.v20130331  │  2 │ 228.3 MiB 
  7 │ cmip5.output.CCCma.CanCM4.decadal1983.mon.atmos.r2i1p1.v20130331    │ 47 │   1.1 GiB 
  8 │ cmip5.output.CCCma.CanCM4.decadal1983.mon.land.r5i1p1.v20130331     │ 11 │  56.4 MiB 
  9 │ cmip5.output.CCCma.CanCM4.decadal1983.mon.landIce.r2i1p1.v20130331  │  6 │  22.6 MiB 
 10 │ cmip5.output.CCCma.CanCM4.decadal1983.mon.ocean.r8i1p1.v20130331    │ 32 │   6.6 GiB 
 11 │ cmip5.output.CCCma.CanCM4.decadal1984.day.atmos.r2i1p1.v20130331    │ 23 │   2.6 GiB 
 12 │ cmip5.output.CCCma.CanCM4.decadal1984.day.landIce.r10i1p1.v20130331 │  2 │ 228.3 MiB 
 13 │ cmip5.output.CCCma.CanCM4.decadal1984.day.seaIce.r3i1p1.v20130331   │  4 │ 456.6 MiB 
 14 │ cmip5.output.CCCma.CanCM4.decadal1980.mon.ocean.r7i1p1.v20130331    │ 96 │  19.8 GiB 
 15 │ cmip5.output.CCCma.CanCM4.decadal1980.mon.ocean.r8i1p1.v20130331    │ 96 │  19.8 GiB 
 16 │ cmip5.output.CCCma.CanCM4.decadal1990.day.atmos.r10i2p1.v20130331   │ 23 │   2.6 GiB 
 17 │ cmip5.output.CCCma.CanCM4.decadal1990.day.atmos.r4i1p1.v20130331    │ 23 │   2.6 GiB 
 18 │ cmip5.output.CCCma.CanCM4.decadal1990.day.atmos.r6i1p1.v20130331    │ 23 │   2.6 GiB 
 19 │ cmip5.output.CCCma.CanCM4.decadal1990.day.land.r5i2p1.v20130331     │  3 │ 342.5 MiB
```
I can filter this to just results from CMIP6.
```console
(seaicecp) root@<container_id>:/workspace# uv run esgpull search project:CMIP6
Found 14217502 datasets.
 id │                                dataset                                 │ #  │   size    
════╪════════════════════════════════════════════════════════════════════════╪════╪═══════════
  0 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r120i1p1f1.Amon.r… │ 45 │ 172.6 MiB 
  1 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r120i1p1f1.Amon.t… │ 45 │ 204.0 MiB 
  2 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r120i1p1f1.Omon.h… │ 45 │ 199.4 MiB 
  3 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r120i1p1f1.Omon.u… │ 45 │   7.5 GiB 
  4 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r120i1p1f1.SImon.… │ 45 │  99.9 MiB 
  5 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r120i1p1f1.day.va… │ 45 │   6.8 GiB 
  6 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r121i1p1f1.Amon.h… │ 45 │   4.2 GiB 
  7 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r121i1p1f1.Amon.p… │ 45 │ 113.1 MiB 
  8 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r132i1p1f1.Amon.h… │ 45 │ 225.7 MiB 
  9 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r132i1p1f1.Amon.h… │ 45 │ 236.8 MiB 
 10 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r131i1p1f1.SImon.… │ 45 │  96.1 MiB 
 11 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r131i1p1f1.day.pr… │ 45 │   4.1 GiB 
 12 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r131i1p1f1.day.rl… │ 45 │   6.5 GiB 
 13 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r131i1p1f1.day.ta… │ 45 │   5.8 GiB 
 14 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r131i1p1f1.day.ua… │ 45 │  22.1 GiB 
 15 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r131i1p1f1.day.zg… │ 45 │  18.1 GiB 
 16 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r133i1p1f1.SImon.… │ 45 │  99.0 MiB 
 17 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r133i1p1f1.SImon.… │ 45 │  99.8 MiB 
 18 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r132i1p1f1.SImon.… │ 45 │  97.8 MiB 
 19 │ CMIP6.CMIP.EC-Earth-Consortium.EC-Earth3.historical.r132i1p1f1.day.rs… │ 45 │   6.0 GiB
```

<a id='esgpull_search_filter'></a>
[back to top](#top)

### Search filtering

While the [ESGF webportal](https://esgf-node.ornl.gov/search) can be tedious for downloading data, I find it incredibly useful for crafting search filters. 
On the left side, I can select CMIP6 as the project, then I am presented with various was to filter the data under the heading "Filter with Facets."
Under the "General" heading, I am always selecting "HighResMIP" as the "Activity ID."

I find the most useful aspect of using the webportal for filtering is that I can see in each dropdown the available values for each facet based on the currently selected search criteria.
For example, if I have selected the project "CMIP6," the Activity ID "HighResMIP," and the institutions "MOHC" and "NERC," when I go to the dropdown for "Sources," I only see the following models listed:
- HadGEM3-GC31-LL
- HadGEM3-GC31-MM
- HadGEM3-GC31-HM
- HadGEM3-GC31-LM
- HadGEM3-GC31-HH
- HadGEM3-GC31-MH

This functionality lets me know what values are possible to search.
Additionally, once I have selected a set of filters, the right side of the page not only shows the list of data available, but also the "Query String."
That contains the exact strings necessary for calling each facet when searching with `esgpull`, such as `activity_id` and `institution_id`.
Using that query string makes it easy to construct the command to use with `esgpull search`.

Rather than retype a search every time I want to change something slightly, I find it easier to put the searches into `bash` scripts which I store in the `esgpull_searches/` directory.
For example, the following script searches for all files with the variable `areacello` (area within a cell that is ocean) for HighResMIP models.
```{literalinclude} ../../esgpull_searches/HRMIP_areacello.sh
:language: bash
```
I have found that the only two nodes which are consistently available at this time are `eagle.alcf.anl.gov` and `esgf-node.ornl.gov`, so I will specifically select these nodes to avoid `esgpull` trying to access a different node and throwing the following error upon trying to download.
```console
...
    |     with map_httpcore_exceptions():
    |          ~~~~~~~~~~~~~~~~~~~~~~~^^
    |   File "/usr/lib/python3.13/contextlib.py", line 162, in __exit__
    |     self.gen.throw(value)
    |     ~~~~~~~~~~~~~~^^^^^^^
    |   File "/workspace/.cvenv/lib/python3.13/site-packages/httpx/_transports/default.py", line 118, in map_httpcore_exceptions
    |     raise mapped_exc(message) from exc
    | httpx.RemoteProtocolError: Server disconnected without sending a response.
    +------------------------------------
ExceptionGroup: Download (1 sub-exception)
See /seaicecp_data/bergybits/log/esgpull-download-2026-05-12_15-30-34.log for error log.
Aborted!
```
When specifying multiple values for a particular facet, such as `data_node`, the syntax `esgpull` expects is to have the values comma-separated, with no spaces.

Running the above script gives the following results.
```console
(seaicecp) root@c11f20a93021:/workspace# bash esgpull_searches/HRMIP_areacello.sh 
Found 46 datasets.
 id │                      dataset                       │ # │   size    │     data_node      
════╪════════════════════════════════════════════════════╪═══╪═══════════╪════════════════════
  0 │ CMIP6.HighResMIP.MOHC.HadGEM3-GC31-LL.control-195… │ 1 │   1.4 MiB │ eagle.alcf.anl.gov 
  1 │ CMIP6.HighResMIP.AWI.AWI-CM-1-1-HR.control-1950.r… │ 1 │ 256.9 MiB │ eagle.alcf.anl.gov 
  2 │ CMIP6.HighResMIP.AWI.AWI-CM-1-1-LR.spinup-1950.r1… │ 1 │  23.4 MiB │ esgf-node.ornl.gov 
  3 │ CMIP6.HighResMIP.AWI.AWI-CM-1-1-LR.hist-1950.r1i1… │ 1 │  23.4 MiB │ eagle.alcf.anl.gov 
  4 │ CMIP6.HighResMIP.MOHC.HadGEM3-GC31-MM.control-195… │ 1 │  31.6 MiB │ eagle.alcf.anl.gov 
  5 │ CMIP6.HighResMIP.MOHC.HadGEM3-GC31-LL.control-195… │ 1 │   1.4 MiB │ esgf-node.ornl.gov 
  6 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.highres-fu… │ 1 │  63.1 MiB │ eagle.alcf.anl.gov 
  7 │ CMIP6.HighResMIP.AWI.AWI-CM-1-1-LR.control-1950.r… │ 1 │  23.4 MiB │ esgf-node.ornl.gov 
  8 │ CMIP6.HighResMIP.MOHC.HadGEM3-GC31-HM.control-195… │ 1 │  31.6 MiB │ esgf-node.ornl.gov 
  9 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-LR.highres-fu… │ 1 │   1.9 MiB │ esgf-node.ornl.gov 
 10 │ CMIP6.HighResMIP.MOHC.HadGEM3-GC31-HM.hist-1950.r… │ 1 │  31.6 MiB │ eagle.alcf.anl.gov 
 11 │ CMIP6.HighResMIP.MOHC.HadGEM3-GC31-MM.highres-fut… │ 1 │  31.6 MiB │ esgf-node.ornl.gov 
 12 │ CMIP6.HighResMIP.MOHC.HadGEM3-GC31-MM.hist-1950.r… │ 1 │  31.6 MiB │ esgf-node.ornl.gov 
 13 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-HR.hist-1950.… │ 1 │  63.1 MiB │ eagle.alcf.anl.gov 
 14 │ CMIP6.HighResMIP.NCAR.CESM1-CAM5-SE-LR.control-19… │ 1 │   1.9 MiB │ esgf-node.ornl.gov 
 15 │ CMIP6.HighResMIP.MOHC.HadGEM3-GC31-LL.highres-fut… │ 1 │   1.4 MiB │ eagle.alcf.anl.gov 
 16 │ CMIP6.HighResMIP.MOHC.HadGEM3-GC31-HM.control-195… │ 1 │  31.6 MiB │ eagle.alcf.anl.gov 
 17 │ CMIP6.HighResMIP.EC-Earth-Consortium.EC-Earth3P-H… │ 1 │  29.8 MiB │ esgf-node.ornl.gov 
 18 │ CMIP6.HighResMIP.MOHC.HadGEM3-GC31-LL.spinup-1950… │ 1 │   1.4 MiB │ esgf-node.ornl.gov 
 19 │ CMIP6.HighResMIP.MOHC.HadGEM3-GC31-MM.spinup-1950… │ 1 │  31.6 MiB │ eagle.alcf.anl.gov
```

<a id='esgpull_queries'></a>
[back to top](#top)

## Add, track, and update queries

Once you have a search that returns the data you want, the next steps are to add, track, then update that query as described in the [`esgpull` documentation](https://esgf.github.io/esgf-download/download/).

To add a search query to the database, change `search` to `add` in the bash script.
```bash
uv run esgpull add \
project:CMIP6 \
activity_id:HighResMIP \
data_node:eagle.alcf.anl.gov,esgf-node.ornl.gov \
variable_id:areacello
```
Then, run the script.
```console
(seaicecp) root@94822df4851d:/workspace# bash esgpull_searches/HRMIP_areacello.sh 
<37ca8c> untracked
│ added    2026-05-12T20:03:29Z
│ updated  2026-05-12T20:03:29Z
└── activity_id: HighResMIP                           
    data_node:   agle.alcf.anl.gov, esgf-node.ornl.gov
    project:     CMIP6                                
    variable_id: areacello                            
👍 1 new query added.
```
This gives the query an ID, in this case, `37ca8c`. 
Queries are untracked by default when they are added to avoid downloading large amounts of unneeded data.
If you are sure this is the query you want, use that ID to tell `esgpull` to track it.
This always results in the system asking to set some options before completing.
```console
(seaicecp) root@94822df4851d:/workspace# uv run esgpull track 37ca8c
For <37ca8c> to become tracked, options must be set.
                         before                         │                         after                          
════════════════════════════════════════════════════════╪════════════════════════════════════════════════════════
 <37ca8c> untracked                                     │ <60d0a8>                                               
 │ added    2026-05-12T20:03:29Z                        │ │ added    2026-05-12T20:03:29Z                        
 │ updated  2026-05-12T20:03:29Z                        │ │ updated  2026-05-12T20:03:29Z                        
 └── activity_id: HighResMIP                            │ └── distrib:     True                                  
     data_node:   agle.alcf.anl.gov, esgf-node.ornl.gov │     latest:      True                                  
     project:     CMIP6                                 │     replica:     True                                  
     variable_id: areacello                             │     retracted:   False                                 
                                                        │     activity_id: HighResMIP                            
                                                        │     data_node:   agle.alcf.anl.gov, esgf-node.ornl.gov 
                                                        │     project:     CMIP6                                 
                                                        │     variable_id: areacello                             
Apply changes? [y/n]: y
👍 <60d0a8> is now tracked.
```
I don't know if there is a way to avoid this or not, but it does change the ID of the query, in this case to `60d0a8`
Once the query is tracked, use the new ID to update it.
This will have `esgpull` use the API to fetch the metadata of each file to download.
If this update results in files that have not been previously downloaded, it will prompt you asking whether to automatically add those new files to the download queue.
```console
(seaicecp) root@94822df4851d:/workspace# uv run esgpull update 60d0a8
<60d0a8> -> 46 files (before replica de-duplication).
Adding 24 new datasets to database.
Adding 24 new files to database.

<60d0a8>: 24  files (1.2 GiB bytes) to download.
Link to query and send to download queue? [y/n/show]: y
<60d0a8> ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
```
If you have more queries that you want to add to the queue before downloading, repeat the above steps for each.

<a id='esgpull_download'></a>
[back to top](#top)

## Downloading data

In the [`esgpull` "Download" documentation](https://esgf.github.io/esgf-download/download/), it is fairly straight-forward to start the download process after [adding, tracking, and updating queries](#esgpull_queries).
Before starting the download, I recommend checking the download queue.
```console
(seaicecp) root@c11f20a93021:/workspace# uv run esgpull show
<60d0a8>
│ added    2026-04-15T14:44:20Z
│ updated  2026-04-15T14:45:09Z
└── distrib:     True                                  
    latest:      True                                  
    replica:     True                                  
    retracted:   False                                 
    activity_id: HighResMIP                            
    data_node:   eagle.alcf.anl.gov, esgf-node.ornl.gov
    project:     CMIP6                                 
    variable_id: areacello                             
    files:       0 / 24                               
    datasets:    0 / 24                               
    size:        0 GiB / 1.2 GiB
```
Running the download command will output the queue again for reference and start downloading the files.
```console
(seaicecp) root@94822df4851d:/workspace# uv run esgpull download
<60d0a8>
│ added    2026-04-15T14:44:20Z
│ updated  2026-04-15T14:45:09Z
└── distrib:     True                                  
    latest:      True                                  
    replica:     True                                  
    retracted:   False                                 
    activity_id: HighResMIP                            
    data_node:   eagle.alcf.anl.gov, esgf-node.ornl.gov
    project:     CMIP6                                 
    variable_id: areacello                             
    files:       0 / 24                               
    datasets:    0 / 24                               
    size:        0 GiB / 1.2 GiB
<32af4f> · 1.4 MiB · 280.0 kiB/s · esgf-node.ornl.gov
<2bd534> · 23.4 MiB · 1.8 MiB/s · eagle.alcf.anl.gov
<17c283> · 11.4 MiB · 884.4 kiB/s · eagle.alcf.anl.gov
<fb4aca> · 31.6 MiB · 2.7 MiB/s · eagle.alcf.anl.gov
<23f4ec> · 31.6 MiB · 1.5 MiB/s · eagle.alcf.anl.gov
<eabd24> · 256.9 MiB · 4.1 MiB/s · eagle.alcf.anl.gov
...
  24/24 01:02  
Downloaded 24 new files for a total size of 1.2 GiB
```
After it completes, I can check the queue again and see that the files are downloaded.
```console
(seaicecp) root@c11f20a93021:/workspace# uv run esgpull show
<60d0a8>
│ added    2026-04-15T14:44:20Z
│ updated  2026-04-15T14:45:09Z
└── distrib:     True                                  
    latest:      True                                  
    replica:     True                                  
    retracted:   False                                 
    activity_id: HighResMIP                            
    data_node:   eagle.alcf.anl.gov, esgf-node.ornl.gov
    project:     CMIP6                                 
    variable_id: areacello                             
    files:       24 / 24                               
    datasets:    24 / 24                               
    size:        1.2 GiB / 1.2 GiB
```
If you were to try and download again, `esgpull` would see all the files in the queue that have been downloaded already and skip those.
This means, if you add a new query that includes data files that you've already downloaded, `esgpull` won't download them again, reducing the chance of accidentally filling up your storage with redundant data files.

<a id='esgpull_download_retry'></a>
[back to top](#top)

### Retrying failed downloads

Sometimes, `esgpull` will fail to download certain files, especially when downloading a large number of them.
This could be due to a number of factors, but likely due to a lapse in network connection.
However, `esgpull` has the functionality built in to keep track of which files failed to download and it will report this at the end of the download output.
```console
...
<ff488c> · 4.5 MiB · 635.0 kiB/s · esgf-node.ornl.gov
<fff7de> · 24.2 MiB · 4.6 MiB/s · eagle.alcf.anl.gov
<ff539a> · 34.1 MiB · 2.3 MiB/s · eagle.alcf.anl.gov
<ff0cc6> · 24.8 MiB · 1.2 MiB/s · eagle.alcf.anl.gov
<ff7e33> · 24.7 MiB · 1.6 MiB/s · eagle.alcf.anl.gov
<fcec76> · 221.2 MiB · 2.5 MiB/s · esgf-node.ornl.gov
  1168/1168 1:54:29 (21 downloads failed)
Downloaded 1168 new files for a total size of 46.6 GiB
```
A simple command sends just the failed downloads back to the queue.
```console
Grey@Audron:seaicecp$ esgpull retry
Sent back to the queue: 21 error
```
Then, starting the download process again will just focus on those missing files.
```console
Grey@Audron:seaicecp$ esgpull download                                           
<aab029>
│ added    2026-04-17T19:24:42Z
│ updated  2026-04-17T19:25:49Z
└── distrib:       True                                                            
    latest:        True                                                            
    replica:       None                                                            
    retracted:     False                                                           
    activity_id:   HighResMIP                                                      
    experiment_id: control-1950, hist-1950                                         
    frequency:     mon                                                             
    project:       CMIP6                                                           
    source_id:     EC-Earth3P-HR, HadGEM3-GC31-HH, HadGEM3-GC31-HM, HadGEM3-GC31-MM
    variable_id:   siconc                                                          
    files:         1173 / 1194                                                     
    datasets:      1 / 16                                                          
    size:          46.7 GiB / 47.9 GiB                                             
<7ea324> · 1.0 MiB · 678.5 kiB/s · esgf-node.ornl.gov
<192f32> · 4.5 MiB · 1.6 MiB/s · eagle.alcf.anl.gov
<0deea2> · 4.7 MiB · 1.4 MiB/s · eagle.alcf.anl.gov
<7f531e> · 1.0 MiB · 609.5 kiB/s · esgf-node.ornl.gov
<7f89da> · 1.1 MiB · 1.1 MiB/s · esgf-node.ornl.gov
<73a00a> · 4.7 MiB · 1.1 MiB/s · eagle.alcf.anl.gov
<80be43> · 1.0 MiB · 2.0 MiB/s · esgf-node.ornl.gov
<8226e6> · 4.6 MiB · 1.2 MiB/s · esgf-node.ornl.gov
<805761> · 4.6 MiB · 846.0 kiB/s · esgf-node.ornl.gov
<825706> · 24.8 MiB · 1.6 MiB/s · esgf-node.ornl.gov
<8273dc> · 24.9 MiB · 1.6 MiB/s · esgf-node.ornl.gov
<82bd08> · 4.5 MiB · 1.5 MiB/s · esgf-node.ornl.gov
<835921> · 4.4 MiB · 1.6 MiB/s · esgf-node.ornl.gov
<837902> · 1.1 MiB · 1,020.7 kiB/s · esgf-node.ornl.gov
<80c0bb> · 225.9 MiB · 1.8 MiB/s · esgf-node.ornl.gov
<d2be71> · 24.5 MiB · 2.7 MiB/s · eagle.alcf.anl.gov
<7ffd13> · 224.1 MiB · 1.6 MiB/s · esgf-node.ornl.gov
<f2cd5f> · 24.2 MiB · 2.6 MiB/s · eagle.alcf.anl.gov
<7a398a> · 224.9 MiB · 1.5 MiB/s · esgf-node.ornl.gov
<83806b> · 224.3 MiB · 1.7 MiB/s · esgf-node.ornl.gov
<8414dc> · 225.2 MiB · 1.7 MiB/s · esgf-node.ornl.gov
  21/21 02:39  
Downloaded 21 new files for a total size of 1.2 GiB
```