# Neboulous Fleet CLI

Simple CLI tool to pretty print fleet files (XML) to console written in Python.

![Starter - TF Ash](images/tf-ash.png)

## Requirements, Installation and Execution

Until the application is packaged and released, you will need to use code from this repository directly.

Clone this repository, or download it as an archive. The minimal requirements are:

- Python 3.8+
- Poetry

To install, run:

```sh
poetry install
```

And to execute, run:

```sh
poetry shell
python3 -m nfcli -i your_file.fleet -p
```

If unsure, run:

```sh
python3 -m nfcli -h
```
