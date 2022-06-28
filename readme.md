# Neboulous Fleet CLI

Simple CLI tool to pretty print fleet files (XML) to console written in Python.

![Starter - TF Ash - column view](images/tf-ash.png)

![Starter - TF Oak - stack view](images/tf-oak.png)

## Requirements, Installation and Execution

Until the application is packaged and released, you will need to use code from this repository directly.

Clone this repository, or download it as an archive. The minimal requirements are:

- Python 3.8+
- Poetry (dependency manager)
- libcairo2 (system library)

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

## Running the bot

- Create a new Application via <https://discord.com/developers/applications>
- Configure `Bot` section and generate a `TOKEN`
- Invite the bot to your server
- Edit `.env.dist` and save it as `.env`
- Run `python3 bot.py` and enjoy your new bot
