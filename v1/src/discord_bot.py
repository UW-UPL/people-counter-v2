import discord
from discord.ext import tasks
import os.path
from yolov7.detect import YoloModel
import config
import cv2
import logging

# setup bot, model, and camera
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
handler = logging.FileHandler(filename=os.path.join("src", "discord.log"), encoding='utf-8', mode='w')

yolo_model = YoloModel(config.confidence)
channel_id = config.channel_id
debug_channel_id = config.debug_channel_id
sleep_interval = 0
is_sleeping = False
debug_mode = True

with open(os.path.join("src", "DISCORD_BOT_TOKEN"), "r") as f:
    token = f.read()


@tasks.loop(minutes=15)
async def update_count():
    global is_sleeping, debug_mode
    await client.wait_until_ready()
    channel = client.get_channel(channel_id)
    debug_channel = client.get_channel(debug_channel_id)
    if not is_sleeping:
        # get image
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        while not ret:
            print("Could not receive frame. Retrying...")
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
        while not cv2.imwrite(os.path.join("src", "img.png"), frame):
            print("Could not write image. Retrying...")

        # run inference
        people_count = yolo_model.run()

        cap.release()
        cv2.destroyAllWindows()

        # update channel name
        if people_count == 1:
            new_name = f"{people_count}-person-in-upl"
        else:
            new_name = f"{people_count}-people-in-upl"
        await channel.edit(name=new_name)

        # update debug channel
        if debug_mode:
            await debug_channel.send(file=discord.File(os.path.join("src", "output.png")))
        print(f"Updated Count: {people_count}")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    update_count.start()


@client.event
async def on_message(message):
    global sleep_interval, is_sleeping, yolo_model, debug_mode
    if message.author == client.user:
        return
    if message.content.startswith("!sleep"):
        try:
            args = message.content.split()[1:]
            if len(args) == 0:
                is_sleeping = True
                await message.channel.send("Channel updates paused.")
            else:
                duration = int(args[0])
                unit = args[1] if len(args) > 1 else "s"
                if unit == "d":
                    sleep_interval = duration * 86400
                elif unit == "h":
                    sleep_interval = duration * 3600
                elif unit == "m":
                    sleep_interval = duration * 60
                else:
                    sleep_interval = duration
                is_sleeping = True
                if sleep_interval == 0:
                    await message.channel.send("Channel updates paused indefinitely.")
                else:
                    await message.channel.send(f"Channel updates paused for {duration} {unit}.")
        except:
            await message.channel.send("Invalid command.")
    elif message.content.startswith("!resume"):
        sleep_interval = 0
        is_sleeping = False
        await message.channel.send("Channel updates resumed.")
    elif message.content.startswith("!confidence"):
        try:
            args = message.content.split()[1:]
            confidence = float(args[0])
            if 0 > confidence > 1.0:
                await message.channel.send("Invalid command: confidence must be between 0.0 and 1.0.")
                return
            yolo_model.conf = confidence

            await message.channel.send(f"Confidence set at:{confidence}.")
        except:
            await message.channel.send("Invalid command.")
    elif message.content.startswith("!debug on"):
        debug_mode = True
        await message.channel.send("Debug mode on.")
    elif message.content.startswith("!debug off"):
        debug_mode = False
        await message.channel.send("Debug mode off.")


client.run(token, log_handler=handler)
