const express = require('express');
const app = express();
const router = express.Router();
const {blueScan} = require('./blueScan');

// Define routes and middleware here
// we basically just want 2 routes:
//  1) the blank form, which scans for all the possible devices
//  2) the route to receive the input via a POST saying what to connect to.

app.set('view engine', 'ejs');
app.use(express.urlencoded({extended: false}));
// for timing out the requests, but the problem is if bluetooth is busy then it complains.
app.use((req, res, next) => {
    res.setTimeout(5000, ()=>{
        console.log('Request has timed out.');
        res.sendStatus(408);
        res.end();
    });
    next();
});

router.route('/')
    .get(async function (req, res) {
        console.log("GET request called");
        res.locals.devices = await blueScan();
        res.render('form');
        res.end();
    })
    .post(async function (req,res) {
        console.log('POST');
        const data = req.body;
        console.log(data);
 	try {	
        	await blueScan(data.choice); 
	} catch(e) {
		console.error(e);
	}

        res.locals.message = `Connection to ${data.choice} Complete!`;  
	// TODO: or catch error/timeout?
	// TODO: in particular, catch for when BT device is not on or in range anymore -- not sure how 

	// use promise.race() to detect a timeout


        res.render('results');
        res.end();
    });

app.use(router);

const PORT = process.env.PORT || 3000;
app.listen(PORT, (err) => {
    if (err) throw err;
    console.log(`Server running on port ${PORT}`);
});
