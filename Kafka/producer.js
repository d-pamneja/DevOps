const {kafka} = require("./client")
const readline = require("readline")

const rl = readline.createInterface({
    input : process.stdin,
    output : process.stdout
})

async function init() {
    try {
        const producer = kafka.producer()
        console.log("Producer Set.")

        await producer.connect()
        console.log("Producer Connected.")

        rl.setPrompt('>')
        rl.prompt()

        rl.on('line',async function(line) {
            const [id,latitude,longitude,zone] = line.split(' ')
            await producer.send({
                partition : zone==="WEST" ? 0 : 1,
                topic : 'rider-updates',
                messages : [
                    {key : `Rider${id}_Location_13:00:00`, value : JSON.stringify({latitude : latitude, longitude : longitude})},
                ]
            })
            console.log("Message sent via Producer.")
        }).on('close',async ()=>{
            await producer.disconnect()
            console.log("Producer disconnected.")
        })
    
    } catch (error) {
        console.log(error)
    }
}

init()