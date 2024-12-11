const {kafka} = require("./client")

async function init() {
    try {
        const admin = kafka.admin()
        console.log("Admin Set.")

        await admin.connect()
        console.log("Admin Connected.")

        await admin.createTopics({
            topics : [{
                topic : 'rider-updates',
                numPartitions : 2,

            }]
        })

        console.log("Topic for rider updates created.")


        await admin.disconnect()
        console.log("Admin Disconnected.")
    } catch (error) {
        console.error(error)
    }
}

init()