const { Client, GatewayIntentBits, ActivityType, PresenceUpdateStatus } = require('discord.js');
const fs = require('fs');

// bot's token is stored in a local file named "TOKEN"
const TOKEN = fs.readFileSync('TOKEN', 'utf8').trim();

const CHANNEL_ID = '1069381357811281943';

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

async function fetchDoorStatus() {
    const fetch = await import('node-fetch').then(module => module.default);
    try {
        const response = await fetch('https://doors.amoses.dev/door-status');
        const data = await response.json();
        
        // Log the status response
        console.log('Fetched door status:', data);

        return data;
    } catch (error) {
        console.error('Error fetching door status:', error);
    }
}

async function updateBotPresence(door1, door2) {
    let statusMessage;
    let botStatus;

    // only "open" if both doors are open
    if (door1 === 'open' && door2 === 'open') {
        statusMessage = 'Both doors open';
        botStatus = PresenceUpdateStatus.online;  // Set bot to online
    } else {
        // anything else, including one door being open, is considered "closed"
        statusMessage = 'Doors closed';
        botStatus = PresenceUpdateStatus.idle;  // Set bot to away/idle
    }

    client.user.setPresence({
        status: botStatus,
        activities: [{
            name: statusMessage,
            type: ActivityType.Watching
        }],
    });

    console.log(`Updated bot presence: ${statusMessage}, Status: ${botStatus}`);
}

async function checkDoorStatus() {
    try {
        const data = await fetchDoorStatus();
        
        if (!data || !data.status) {
            console.error('Invalid door status response:', data);
            return;
        }

        const door1 = data.status.door1;
        const door2 = data.status.door2;

        const channel = await client.channels.fetch(CHANNEL_ID, { force: true });
        console.log('Fetched channel name:', channel.name);

        const changeChannelName = async (newName) => {
            console.log(`Attempting to update channel name to "${newName}"...`);
            channel.setName(newName);
        };

        // update channel name
        if (door1 === 'open' && door2 === 'open') {
            if (channel.name !== 'upl-doors-open') {
                await changeChannelName('upl-doors-open');
            } else {
                console.log('Channel name is already "upl-doors-open"');
            }
        } else {
            if (channel.name !== 'upl-doors-closed') {
                await changeChannelName('upl-doors-closed');
            } else {
                console.log('Channel name is already "upl-doors-closed"');
            }
        }
        await updateBotPresence(door1, door2);

    } catch (error) {
        if (error.code === 50013) {
            console.error('Error: Missing permissions to update channel name.');
        } else {
            console.error('Error updating channel:', error);
        }
    }
}

client.on('rateLimit', (info) => {
    console.warn(`Rate limit hit: ${info.timeout}ms timeout after ${info.limit} requests.`);
});

client.once('ready', () => {
    console.log(`Logged in as ${client.user.tag}!`);
    
    // Check door status every 60 seconds
    setInterval(checkDoorStatus, 60000);
});

client.login(TOKEN);
