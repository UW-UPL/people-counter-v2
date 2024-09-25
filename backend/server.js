const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const port = 1984; // chosen by ben f

app.use(bodyParser.json());

app.use((req, res, next) => {
  res.header("Access-Control-Allow-Origin", "*"); // turn on CORS so we can access this from wherever
  res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
  next();
});

// this isn't my favorite way of doing this! on a server restart we'll lose the door statuses & they'll appear closed. probably better to store this in a local file or a database
let doorStatuses = {
  door1: null,
  door2: null,
};

// endpoint for door 1 open
app.post('/door1/open', (req, res) => {
  doorStatuses.door1 = 'open';
  console.log('Door 1 opened');
  res.status(200).json({ message: 'Door 1 is now open', status: doorStatuses });
});

// endpoint for door 1 close
app.post('/door1/close', (req, res) => {
  doorStatuses.door1 = 'closed';
  console.log('Door 1 closed');
  res.status(200).json({ message: 'Door 1 is now closed', status: doorStatuses });
});

// endpoint for door 2 open
app.post('/door2/open', (req, res) => {
  doorStatuses.door2 = 'open';
  console.log('Door 2 opened');
  res.status(200).json({ message: 'Door 2 is now open', status: doorStatuses });
});

// endpoint for door 2 close
app.post('/door2/close', (req, res) => {
  doorStatuses.door2 = 'closed';
  console.log('Door 2 closed');
  res.status(200).json({ message: 'Door 2 is now closed', status: doorStatuses });
});

// grabbing the status of both doors
app.get('/door-status', (req, res) => {
  res.status(200).json({ status: doorStatuses });
});

// funny message for the root endpoint
app.get('/', (req, res) => {
  res.send('<b>wow upl door endpoint port 443</b>');
});

// localhost:1984
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
