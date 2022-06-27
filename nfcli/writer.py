from nfcli.model import Fleet


def write_fleet(fleet: Fleet, output_prefix: str):
    for idx, ship in enumerate(fleet.ships):
        filename = output_prefix + str(idx)
        pass
