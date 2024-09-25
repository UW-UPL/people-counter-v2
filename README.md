# 🚪 People Counter v2

Here's the new people counter setup! Subject to change.

### Home Assistant/Zigbee

We have two Aqara door/window sensors. These communicate over a protocol called Zigbee. The rpi can't interact with this protocol by default, so we have a special Zigbee sensor plugged into the pi to allow it to see these signals. No need for a propriatary hub!

The pi is running [Home Assistant](https://www.home-assistant.io/]), which allows it to read the Zigbee signals using [ZHA](https://www.home-assistant.io/integrations/zha/]). Then, whenever the status of either sensor changes, it runs one of four REST commands. Becauase of how Home Assistant is currently set up, these have to be defined in its `configuration.yaml`, which I've included [in this repo](./home-assistant/configuration.yaml). They're named intuitively: `door1_opened`, `door1_closed`, `door2_opened`, and `door2_closed`.

### The Elephant in The Room (Backend)

So, UWNet and eduroam both employ access point isolation such that both devices on the broader internet & local ones alike are unable to see any others on the network. (This makes sense, as anyone on the network would be able to see _everyone's devices!_) Because of this,web servers aren't able to directly query Home Assistant to see the status of its devices.

To work around this, I threw together a really simple Express server [in the backend folder](./backend/) that caches any live events it receives from the pi. So, when the pi announces that door 1 has been opened, the backend will hang onto that and rebroadcast it when someone checks the status. It'll return an object in this format:

```json
{
  "status": {
    "door1": "open",
    "door2": "closed"
  }
}
```

For reference, `door1` is the one at the front of the UPL (that faces into the lobby), and `door2` is the one at the back (that faces the balcony).

...this probably isn't the best way of doing things, as there's the extra redundancy of having a server that just repeats what the pi says. If the UPL ever gets the ability to have its LAN devices publicly accessible, this server can be removed.

(Or, we could put both the pi and the server on a Tailnet. The rpi is already on one!)

### Discord Bot

Queries the endpoint and, if both doors are open, sets the name of the channel to `upl-doors-open`. If either door is closed, it sets the name to `upl-doors-closed`. It updates every minute.

There's a weird issue where sometimes it'll skip updating the channel name for a bit. Not sure if it's a caching issue...?
