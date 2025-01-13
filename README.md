## HbbTV Attack Toolkit

This is a modular attack toolkit developed within the "Exploiting SmartTVs using the HbbTV Protocol" diploma thesis.

### How to run

It is required to have ``Python 3.6`` or newer installed.

1. Create a new virtual environment
```bash
$ python3 -m venv .
```
2. Download and install the required packages from ``requirements.txt``
```bash
$ pip install -r requirements.txt
```
3. Run the attack toolkit
```bash
$ python attack_toolkit.py
```

Now you should have the toolkit listening on port ``5000``.

### How do I get it running on a smart TV?

To get the toolkit running on a smart TV, you need to create a own DVB stream with an custom application information table (AIT) injected and modulate it to the smart TV. For more instructions, follow the [official HbbTV guide](https://developer.hbbtv.org/guide/launching-hbbtv-applications-from-a-broadcast-channel/building-a-broadcast-ait/) or the steps from the thesis.