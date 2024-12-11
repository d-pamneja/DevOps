const {kafka} = require("./client")
const NodeGeocoder = require('node-geocoder');

const geocoder = NodeGeocoder({
    provider: 'openstreetmap',
    formatter: null // 'formatter' can be used to format the result
});
  
async function getLocation(latitude, longitude) {
    try {
        const [result] = await geocoder.reverse({ lat: latitude, lon: longitude });
        
        return {
            formattedAddress: result.formattedAddress,
            country: result.country || 'Unknown',
            zipcode: result.zipcode || 'Unknown',
        };
    } catch (error) {
        console.error('Geocoding error:', error);
        return null;
    }
}

const group = process.argv[2]
async function init() {
    try {
        const consumer = kafka.consumer({
            groupId : `location-parser-${group}`
        })
        console.log("Consumer Set.")

        await consumer.connect()
        console.log("Consumer Connected.")

        await consumer.subscribe({
            topics : ['rider-updates'],
            fromBeginning : false
        })
        console.log("Consumer subscribed to topic 'rider-updates'.")

        await consumer.run({
            eachMessage : async({topic,partition,message,heartbeat,pause}) => {
                const messageValue = JSON.parse(message.value.toString());
                const locationDetails = await getLocation(
                    parseFloat(messageValue.latitude), 
                    parseFloat(messageValue.longitude)
                );
                
                console.log(`Topic [${topic}] : Partition [${partition}] : Group : [${group}]`);
                console.log('Original Location:', messageValue);
                console.log('Geocoded Location:', locationDetails);
            }
        })
        console.log("Consumer ran successfully.")

        // await new Promise(() => {}) // Keep running indefinitely to listen to messages
    } catch (error) {
        console.log(error)
    }
}

init()