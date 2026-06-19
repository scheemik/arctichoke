# Jupyter Notebook Test

This guide details how to test whether the Jupyter notebook server is running correctly after {doc}`Starting the Container <start_container>`.

## Contents

- [Testing the container's Jupyter server](#testing-the-containers-jupyter-server)
- [Troubleshooting](#troubleshooting)

---

## Testing the container's Jupyter server
[back to top](#jupyter-notebook-test)

Once the container has been started and the Jupyter server is running, open the `jupyter_test.ipynb` notebook in VSCodium.
That notebook has instructions on how to run it, however more details are given below.

A raw-text cell beneath the heading "Select the kernel" has the following URL which specifies the location at which the local system can attach to the Jupyter kernel that the container has started.
```
http://127.0.0.1:8889/lab
```
Copy that address.

Next, click the button in the top right of the notebook that says "Select Kernel" or the name of a previous kernel, something like "Python 3 (ipykernel)."
This will bring up a dialogue near the top of the VSCodium window asking you to "Select kernel for 'jupyter_test.ipynb'."
Choose the option, "Select Another Kernel..." **even if it shows a kernel available from a previous session.**
This is important because, every time the container restarts, the exact identifier of the container is different.
So, if you try to use a kernel that you attached to the last time you ran the container, VSCodium will hang, spinning in place looking for that kernel which no longer exists.

Then, choose "Existing Jupyter Server".
If you have run the Jupyter sever before, you will see a list of existing options.
For the reason stated above, none of these will work and I suggest you hit the "x" at the right of each one so the dialogue doesn't get crowded.
Once that is done, select "Enter the URL of the running Jupyter sever."
Paste in the URL you copied earlier and hit "Enter."

This will bring up the dialogue:
> "Connecting over HTTP without a token may be an insecure connection. Do you want to connect to a possibly insecure server?" 

At the bottom of the `Containerfile`, it is specified that there is no token or password for the Jupyter server.
Select "Yes." 

The dialogue will then ask if you want to specify a name for the server.
As the server will disappear after the container closes, I generally just hit "Enter" to select the default name.
Then, select the Jupyter Kernel.
There should only be one available to choose.
If you have the terminal where you started the container visible, you will see some activity there.

Next, click "Run All" near the top left of the notebook.
Go through the notebook to ensure that the output of the cells makes sense.
If everything checks out, then close the notebook.
You will be greeted with the following dialogue box.
> "Do you want to save the changes you made to `jupyter_test.ipynb`?
> Your changes will be lost if you don't save them."

Since the point of the notebook is to test whether the outputs make sense, it is important not to save the outputs. 
Click "Don't Save."

Now, upon opening any other notebook, you should be able to select the same kernel as the one that you just tested.

---

## Troubleshooting
[back to top](#jupyter-notebook-test)

If you click "Run All" in the notebook and nothing happens try restarting the container:
- Close the notebook, selecting "Don't save" when prompted.
- Stop the container by clicking in to the terminal where the Jupyter server is running and hitting "control+C" twice in a row.
- Start the container again and wait for the Jupyter server to start up.
- Open `jupyter_test.ipynb` and try the above steps again.

If that still doesn't work, try restarting VSCodium:
- Close all `.ipynb` files in VSCodium. When closing `jupyter_test.ipynb`, select "Don't Save" when prompted.
- Stop the container by clicking in to the terminal where the Jupyter server is running and hitting "control+C" twice in a row.
- Quit out of VSCodium, then reopen it.
- Start the container again and wait for the Jupyter server to start up.
- Open `jupyter_test.ipynb` and try the above steps again.

If the server is taking a really long time to execute the cells of the `jupyter_test.ipynb` notebook, especially if you see the following output in the terminal where you started the container:
```console
[W 2026-06-04 18:30:25.298 ServerApp] The websocket_ping_timeout (90000) cannot be longer than the websocket_ping_interval (30000).
    Setting websocket_ping_timeout=30000
```
Try the following:
- Click the "Interrupt" button near the top left of the notebook.
    - This will cause that button to change back into "Run All".
- Click the "Restart" button near the top left of the notebook.
    - Wait for the restart dialogue that pops up near the bottom right of the VSCodium window to disappear.
- Try clicking the "Run All" button again.