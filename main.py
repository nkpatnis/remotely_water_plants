from machine import Pin
import asyncio
from lib.utils import Record, get_system_datetime
from lib.wifi import WiFi
from lib.telegram import TelegramBot
from lib.ntptime import settime
from dht import DHT11
from secrets import AUTHORIZED_USERS, BOT_TOKEN, PASS, SSID


WATER_DURATION = 90
MIN_H = 55
OFF = 1
ON = 1


def is_authorized(chat_id):
    return str(chat_id) in AUTHORIZED_USERS


sensor = DHT11(Pin(14))
pump = Pin(15, Pin.OUT)
record = Record()
wifi = WiFi(SSID, PASS)

def setup():
    print("Setting Up")
    pump.value(OFF)  # making sure pump is in off state

    # must not be called under asyncio as they use time.sleep
    # Connect to internet and sync RTC
    wifi.connect()
    settime()


def get_sensor_data():
    sensor.measure()
    temperature = sensor.temperature()
    humidity = sensor.humidity()
    return temperature, humidity


def get_now():
    formatted_date, formatted_time = get_system_datetime()
    return f"{formatted_date} {formatted_time}"


def get_status():
    # Read the file
    data = record.read_from_file()
    temperature, humidity = get_sensor_data()
    data.update(
        {
            "count": data.get("count", 0) + 1,
            "total_auto_run": data.get("total_auto_run", 0),
            "hdt": humidity,
            "temp": temperature,
        }
    )

    return data


async def maintain_water(chat_id, bot):
    # NOTE: must run for some fixed time and turn off
    await turn_on(chat_id, bot)


def get_formatted_data(data):
    return "\n".join([f"{key} : {value}" for key, value in data.items()])


async def auto_action(chat_id, bot):
    try:
        data = get_status()
        # Increment the count
        data["total_auto_run"] = data.get("total_auto_run", 0) + 1

        await maintain_water(chat_id, bot)

        # Update the file
        record.write_to_file(data)
        bot.send(chat_id, f"{get_formatted_data(data)}")
        bot.send(chat_id, "Auto run complete.")
    except Exception as e:
        print("An error occurred:", e)
        bot.send(chat_id, "Something Went Wrong ->")
        bot.send(chat_id, str(e))


async def turn_on(chat_id, bot):
    bot.send(chat_id, "ON started")
    pump.value(ON)
    await asyncio.sleep(WATER_DURATION)
    pump.value(OFF)
    bot.send(chat_id, "ON complete.")


async def turn_off(chat_id, bot):
    bot.send(chat_id, "OFF started")
    pump.value(OFF)
    bot.send(chat_id, "OFF complete.")


# Define your message handler
def message_handler(
    bot, msg_type, chat_name, sender_name, chat_id, text, message_object
):
    print(f"Message from {sender_name}: {text}")
    if not is_authorized(chat_id):
        if text == "/start":
            bot.send(chat_id, f"Unauthorized user. [id: {chat_id}]")
            return

        bot.send(chat_id, "Unauthorized access.")
        return

    # Reply to the message
    if text == "/start":
        bot.send(chat_id, "Hello! I'm your IoT bot.")

        msg_text = f'Your chat_id is {chat_id} \
        \nNow: {get_now()} \
        \nCommands are: \
        \n/status -> to get system status \
        \n/run_auto -> single auto run \
        \n/on -> turn on water for 1 min \
        \n/off -> turn off water \
        '
        bot.send(
            chat_id,
            msg_text,
        )

    elif text == "/status":
        data = get_status()
        bot.send(chat_id, f"System is running normally.\n{get_formatted_data(data)}")

    elif text == "/run_auto":
        asyncio.create_task(auto_action(chat_id, bot))

    elif text == "/on":
        asyncio.create_task(turn_on(chat_id, bot))

    elif text == "/off":
        asyncio.create_task(turn_off(chat_id, bot))
    else:
        bot.send(chat_id, f"Sorry unable to understand.")


# Main program
setup()

# Create the bot
bot = TelegramBot(BOT_TOKEN, message_handler)

# Initialize the async event loop
loop = asyncio.get_event_loop()

# Start the bot
loop.create_task(bot.run())

# Run the event loop
loop.run_forever()
