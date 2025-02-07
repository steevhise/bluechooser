const express = require('express');
const app = express();
const router = express.Router();
const {blueScan, sleep} = require('./blueScan');
const timeout = 5;  // in seconds

// Define routes and middleware here
// we basically just want 2 routes:
//  1) the blank form, which scans for all the possible devices
//  2) the route to receive the input via a POST saying what to connect to.

app.set('view engine', 'ejs');
app.use(express.urlencoded({extended: false}));
// for timing out the requests, but the problem is if bluetooth is busy then it complains.
// we don't need this as we're doing the timeout ourselves
/*app.use((req, res, next) => {
    res.setTimeout(9000, ()=>{
        console.log('Request has timed out.');
        res.sendStatus(408);
        // res.end();
        return;
    });
});*/

router.route('/')
    .get(async function (req, res) {
        console.log("GET request called");
        res.locals.devices = await blueScan();
        res.render('form');
        res.end();
    })
    .post(async function (req,res) {
        const data = req.body;
        console.log('POST request', data.choice);
        let r = await Promise.race([sleep(timeout * 1000), blueScan(data.choice)])
        console.log(r);
        if (r === 'times up!') {
            res.locals.message = `Connection to ${data.choice} has timed out!`;
        } else {
            res.locals.message = `Connection to ${data.choice} Complete!`;  // TODO: or catch error/timeout?
        }
        res.render('results');
        res.end();
    });

app.use(router);

const PORT = process.env.PORT || 3000;
app.listen(PORT, (err) => {
    if (err) throw err;
    console.log(`Server running on port ${PORT}`);
});
