import asyncio
from bleak import BleakScanner


async def discover():
    print("scanning for 5 seconds, please wait...")

    devices = await BleakScanner.discover(
        return_adv=True
        # service_uuids=args.services,
        # cb=dict(use_bdaddr=args.macos_use_bdaddr),
    )

    print("ok, we got the devices...")
    return devices



