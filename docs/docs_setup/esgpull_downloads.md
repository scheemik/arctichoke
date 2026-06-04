<a id='top'></a>
# Downloading model data with `esgpull`

The instructions below show how to use `esgpull` within the container to download CMIP6 HighResMIP model data.
For more details on how the architecture of this project was developed, see the {doc}`Initial Setup <initial_setup>` guide. 

## Contents

- [Why `esgpull`?](#esgpull_why)
- [Installing `esgpull`](#esgpull_install)

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

- ESGF webportal is great for searching
- Globus can download a lot of data in a reasonable way

I decided to use [`esgpull`](https://esgf.github.io/esgf-download/quickstart/) for this project as it offers a way to programmatically download data from HighResMIP models. 
This means, I can write a script that downloads exactly the data I want and can assume that the data will be in a predictable, and expandable, directory structure, making it much more straight-forward to write functions that interact with model data that can apply to new model data as it is downloaded.
To get an idea of what the file structure created by `esgpull` looks like, below is a truncated example.

```{include} data_dir_structure.md
```
