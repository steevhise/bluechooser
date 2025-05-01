const {createBluetooth} = require('node-ble')
const {bluetooth} = createBluetooth()
const Debug = require('debug')('bluetooth');
// const defaultTarget = 'Membrillo';

const blueScan = async (target = '', target2 = '') => {

    Debug('scanning for %s...%s', target + ' ' + target2)
    if(target === target2) {
	    target2 = '';
    }
    const deviceInfo = [];
    const adapter = await bluetooth.defaultAdapter()

    if (!await adapter.isDiscovering())
        await adapter.startDiscovery()

    // otherwise, we ARE discovering...
    const devices = await adapter.devices();
    Debug(devices);

    let device= {};

    for (const d of devices) {
        device = await adapter.getDevice(d);
        const name = await device.getAlias();
        const paired = await device.isPaired();
        const connected = await device.isConnected();
        Debug(d,name,paired);

	if(!target && !target2) {
           // we're just scanning, not connecting.
	   Debug('just scanning, not connecting');   
	}

        if((target) && (name === target)) {
            try {
                if (!await device.isPaired()) {
                    await device.pair();
		    paired = true;
                    Debug('paired with %s', name);
		}
                if (!await device.isConnected()) {
                    await device.connect();   // TODO: catch error?
                    Debug('connected to speaker 1: %s', name);
		    connected = true;
		} else {
                    Debug('already connected to speaker 1 "%s"', name);
		}
            } catch(e) {
                console.log('something wrong connecting with first speaker ' + target, e.text);
                return 'timeout';
            }
        }
	else if((target2) && (name === target2)) {
            try {
                if (!await device.isPaired()) {
                    await device.pair();
		    paired = true;
                    Debug('paired with %s', name);
	        }
                if (!await device.isConnected()) {
                    await device.connect();   // TODO: catch error?
                    Debug('connected to speaker 2: %s', name);
		    connected = true;
		} else {
                    Debug('already connected to speaker 2 "%s"', name);
		}
            } catch(e) {
                console.log('something wrong connecting with second speaker ' + target2, e.text);
                return 'timeout';
            }
	}

	deviceInfo.push({
              id: d,
              name,
              paired,
              connected
	});
    }

    Debug('devices: %o', deviceInfo);
    await adapter.stopDiscovery()
    return deviceInfo;
}

const sleep = async (time) => {
    return new Promise((resolve) => setTimeout(() => { return resolve('timeout')}, time));
}

// find which device is connected
const findConnected = async () => {
    const devices = await blueScan()
    return devices.find((entry) => { return entry.connected === true }).name
}


exports.blueScan = blueScan;
exports.sleep = sleep;
exports.findConnected = findConnected;

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

