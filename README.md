font-tool
=========

Check if b2g supports a particular locale font-wise.

You'll need to update the moztt and base submodules to the revisions you test, and run the script as

    python buildfonts.py path/to/mozilla/repo ab-CD

The tools relies on font-config to do the heavy lifting.
The tool is currently only catching the Regular font weights, etc.
