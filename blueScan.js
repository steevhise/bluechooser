const {createBluetooth} = require('node-ble')
const {bluetooth} = createBluetooth()
const Debug = require('debug')('bluetooth');
const defaultTarget = 'Membrillo';

const blueScan = async (target = '') => {

    Debug('scanning for %s...', target)
    const deviceInfo = [];
    const adapter = await bluetooth.defaultAdapter()

    if (!await adapter.isDiscovering())
        await adapter.startDiscovery()

    // otherwise, we ARE discovering...
    const devices = await adapter.devices();

    for (const d of devices) {
        const device = await adapter.getDevice(d);
        const name = await device.getAlias();
        const paired = await device.isPaired();
        const connected = await device.isConnected();
        // Debug(d,name);
        deviceInfo.push({
            id: d,
            name,
            paired,
            connected
        });

        if((target) && (name === target)) {
            if (!await device.isPaired())
                await device.pair();
            Debug('paired with %s', target);
            if (!await device.isConnected())
                await device.connect();   // TODO: catch error?
            Debug('connected to %s', name)
            console.log('connected to ' + name);
            break;
        }
    }

    // Debug('devices: %o', deviceInfo);
    await adapter.stopDiscovery()
    return deviceInfo;
}

exports.blueScan = blueScan;

 // how you'd use this...
/*
blueScan('hiSE')
    .then( (result) => {
        Debug(result);
    })
    .catch((e) => {
        throw 'something went wrong' + e;
    })
    .finally(() => {
        Debug('ok');
        process.exit(1)
    });

*/

