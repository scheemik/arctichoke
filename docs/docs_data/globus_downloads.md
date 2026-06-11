<a id='top'></a>
# Downloading model data with Globus

For this project, I ultimately decided to {doc}`download model data with esgpull <esgpull_downloads>` instead of Globus. 
Nonetheless, below I document the process of setting up Globus and using it to download a sample of data for one model.

From the [ESGF User Tutorials page](https://esgf.github.io/esgf-user-support/user_guide.html#login-openid) I found that I can just use my York University account. 
It gave me the option to link to another Globus account, but I didn't have one already. 

In making the account, I needed to allow Django Backend to:
- View your email address
- View your identity
- Full access to Globus Search
- View identity details
- Manage data using Globus Transfer

I then installed the [Globus Connect Personal](https://www.globus.org/globus-connect-personal) application on my laptop. 
During that installation, I needed to allow Globus Web App to:
- Search for data using your identities and groups
- Manage data using Globus Transfer
- View the identities in your Globus account
- Manage your Globus groups (v2)

Upon installing the app and trying to log in, I needed to allow Globus Connect Personal Setup to:
- View information about your linked identities
- View your identity
- View identity details
- Create Globus Connect Personal collections in the Globus Transfer service

I gave this instance the label `<laptop_name>.local`. 

For the Collection Details, I entered:
- Owner Identity
    - `<user>@yorku.ca`
- Collection Name
    - `SICP_GLOBUS`
- Description
    - `<laptop_name>.local`
- High Assurance
    - No

After this, I then had a menu bar icon for Globus. 
I clicked that icon and opened up the settings. 
Under "Access", I added the `BERGY_BITS` volume, specifically the `seaicecp_data` folder and made it "writeable". 
It automatically added my home directory `/Users/<user>` as writeable. 
I'll leave that for now, but I'll consider denying that in the future as I don't see any reason it would need to write in that location. 

Then, I went to the ESGF data portal and did the following search:
```
Query String: latest = true AND (activity_id = HighResMIP) AND (experiment_id = hist-1950) AND (variable_id = siconc) AND (source_id = EC-Earth3P-HR) AND (data_node = aims3.llnl.gov OR esgf-data1.llnl.gov OR esgf-data2.llnl.gov OR esgf-node.ornl.gov OR eagle.alcf.anl.gov) AND (frequency = mon)
```

I added that data to the cart, and then went to view the cart. 
At the bottom, there is a section called "Download Your Cart." 
I'm using the "Globus" option, and I clicked on the "Manage Collections" button. 
This brought up a window in which I searched for the "Collection Name" I set above I found it:
- Name: `SICP_GLOBUS`
    - ID: `a1c86329-43f7-11f1-9908-0afffe4617ab`

I added that, then selected the "Set Path" button which brought up the notice: 
> "You will be redirected to set the path for the collection. Continue?" 

Upon continuing, this brought me to a different page where I clicked through a file system to select `/Volumes/BERGY_BITS/seaicecp_data/` as the path. 
I named this path `SICP_BERGY_BITS`. 
Back at the cart, I clicked the "Transfer" button which gave me the notice: 
> "You will be redirected to obtain globus tokens. Continue?"

After continuing, I needed to allow React Client to:
- Manage data using Globus Transfer
- View your email address
- View your identity
- View identity details 

Then, the page said the transfer was successful and I noticed the menu bar for Globus now has a spinning wheel. 
I clicked on it, then "Web: Activity" which opened a tab in my browser where I could then see the download progress. 
Looking in the `/Volumes/BERGY_BITS/seaicecp_data/` directory, I can see some files being added there. 
It is a completely flat directory structure, but the file names are constructed in a consistent way so hopefully, it should be relatively easy to write code to bring up the correct files for the data I want.