// Create a discord bot using OpenAI API that interacts on the Discord Server
require('dotenv').config();

//prepare to connect to the discord API
const { Client, GatewayIntentBits } = require('discord.js');
const client = new Client({ intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
]})

// prepare connection to open API
//const { Configuration , OpenApi} = require('openai');
//const configuration = new Configuration({
 //   organization: process.env.OPENAI_ORG,
 //   apiKey: process.env.OPENAI_KEY
//});
//const openai = new OpenApi(configuration);

// check for when a message on discord is send
client.on('messageCreate', async function(message){
    try {
        console.log(message.content);
        message.reply(`You said: ${message.content}`);
    }catch(err){
        console.log(err)
    }
});

// log the bot into discrd
client.login(process.env.BRUDER_TOKEN);
console.log("ChatGPT Bot is Online on Discord")