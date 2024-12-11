const {Kafka} = require("kafkajs")

exports.kafka = new Kafka({
    clientId : "my-app",
    brokers : ["localhost:9092"], // Location where the kafka service is running i.e. you IP Address/Localhost and then the port
})
