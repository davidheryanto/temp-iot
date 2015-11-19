var Client = require("ibmiotf").IotfDevice;
var config = {
"org" : "km4ts7",
"id" : "1234",
"type" : "atrack",
"auth-method" : "token",
"auth-token" : "DE5vHelsELG1SH46Ba"
};

var client = new Client(config);

client.connect();

client.on("connect", function () {
//publishing event using the default quality of service
client.publish("status","json",'{"d" : { "cpu" : 60, "mem" : 50 }}');

//publishing event using the user-defined quality of service
var myQosLevel=2
client.publish("status","json",'{"d" : { "cpu" : 60, "mem" : 50 }}', myQosLevel);
});
