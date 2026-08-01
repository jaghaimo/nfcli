# Deployment

## Preparing machine

Assuming a Debian Trixie OS, run the following:
```sh
# As `root`:
dpkg --add-architecture i386
apt update
apt install python3-poetry sudo steamcmd libcairo-2
adduser hazel

# Log in as `hazel`, and run:
steamcmd  # log in to Steam (only if you want workshop integration)
ln -s .steam/steam Steam
```

## Running bot

Download latest code (`master` branch) and extract it.
Edit `.env.dist` and save as `.env`.
Run `poetry install` and finally you can start the bot with command `poetry run bot`.
You may want to start a `screen` first, so the bot runs even while you log out.

# Update script

To ease the update I have a script I run on every update:
```sh
killall screen
wget https://github.com/jaghaimo/nfcli/archive/refs/heads/master.zip
rm -rf nfcli-master
unzip master.zip
cp env nfcli-master/.env
rm master.zip
cd nfcli-master
make steam wiki
```
