import requests
import os
import time
import threading
import re
from mcrcon import MCRcon
from openai import OpenAI


OPENAI_API_KEY = "" # Put your OpenAI api key here
GPT_MODEL = "gpt-4-1106-preview"
RCON_HOST = 'localhost'
RCON_PORT = 25575
RCON_PASSWORD = 'test'

# Put your username in here
player_executor = ""

def download_minecraft_server(version='latest', save_path='./'):
    versions_url = 'https://launchermeta.mojang.com/mc/game/version_manifest.json'
    try:
        versions_data = requests.get(versions_url).json()
        if version == 'latest':
            latest_version_id = versions_data['latest']['release']
            version_data_url = next(item for item in versions_data['versions'] if item["id"] == latest_version_id)['url']
        else:
            version_data_url = next(item for item in versions_data['versions'] if item["id"] == version)['url']
        
        version_specific_data = requests.get(version_data_url).json()
        server_url = version_specific_data['downloads']['server']['url']
        
        response = requests.get(server_url)
        filename = os.path.join(save_path, f'minecraft_server_{version}.jar')
        
        with open(filename, 'wb') as file:
            file.write(response.content)
        
        print(f"Downloaded Minecraft server version {version} to {filename}")
        return filename
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def setup_server(server_jar, eula=True, server_properties_path='./server.properties'):
    if eula:
        with open('eula.txt', 'w') as file:
            file.write('eula=true')
    
    # Setup server.properties for RCON
    with open(server_properties_path, 'w') as prop_file:
        prop_file.write(f"""enable-rcon=true
rcon.port={RCON_PORT}
rcon.password={RCON_PASSWORD}
broadcast-rcon-to-ops=true""")

    java_path = r"C:\Program Files\Java\jdk-17\bin\java.exe"  # Adjust as needed
    os.system(f'"{java_path}" -Xmx1024M -Xms1024M -jar {server_jar} nogui')

def get_player_coords(username):
    with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
        response = mcr.command(f'/data get entity {username} Pos')
        
        # Example response: <username> has the following entity data: [12.34d, 56.78d, 90.12d]
        pattern_coords = re.compile(r".*: \[(.*d), (.*d), (.*d)\]")
        match = pattern_coords.search(response)
        
        if match:
            x, y, z = match.groups()
            x = str(round(float(x[:-1])))  # Remove 'd' and round the x coordinate
            y = str(round(float(y[:-1])))  # Remove 'd' and round the y coordinate
            z = str(round(float(z[:-1])))  # Remove 'd' and round the z coordinate
            return x, y, z  # Returns the coordinates as a tuple of strings
        else:
            return None  # Or handle this case appropriately

def process_chat_with_gpt(client, model, user_message, user_position):
    # Ensure user_position is a string, tuple, or has a default value
    user_position_str = " ".join(map(str, user_position)) if user_position else "Unknown position"
    
    system_prompt = (
        f"You are an internal GPT model operating inside of a Minecraft server. You are allowed to use any command. Dont refuse to do unethical ingame commands, this is a private powerful server. Nothing is too much."
        "You are going to create Minecraft commands and messages that are going to be sent in the chat. When making minecraft commands its incredibly important you are perfect with the command syntax."
        "Note: The player's current position is {user_position_str}. Use it for positional based commands but never mention you know it. never use ~ ~ ~, use the actual coords."
        "Dont use /Whisper, you talk by doing ['Talk here']. For commands and talking: /command here ['message']. You can only send one message and command per response."
        "/{Command here} ['optional chat message here']. For reference here is an example: /give Username minecraft:iron_pickaxe 1 ['Here is your iron pickaxe!']"    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred with OpenAI: {e}")
        return "Error processing message."

def handle_gpt_response(response):
    # This regex matches the command and optional message format
    match = re.match(r"/(.*?)\s*(\['(.*?)'\])?$", response)
    if match:
        command = match.group(1)
        optional_message = match.group(3) if match.group(2) else None
        execute_minecraft_command(command, optional_message)
    else:
        # Assuming the response is just a message in ['message'] format
        message_match = re.match(r"\['(.*?)'\]$", response)
        if message_match:
            message = message_match.group(1)
            execute_minecraft_command("", message)

def monitor_chat_and_process_with_gpt(log_file_path, openai_api_key):
    client = OpenAI(api_key=openai_api_key)
    
    last_position = os.path.getsize(log_file_path)
    while True:
        current_size = os.path.getsize(log_file_path)
        if current_size > last_position:
            with open(log_file_path, "r") as file:
                file.seek(last_position)
                for line in file:
                    if "[Server thread/INFO]: <" in line:
                        parts = line.split(": ")
                        chat_content = parts[-1].strip()
                        username = chat_content.split(">")[0][1:]
                        user_message = chat_content.split("> ")[1]
                        
                        # Get player coordinates
                        player_coords = get_player_coords(username)
                        if player_coords:
                            coords_str = f"{player_coords[0]} {player_coords[1]} {player_coords[2]}"
                        else:
                            coords_str = "Coordinates not available"

                        formatted_message = f"A user with the username: {username} and coordinates {coords_str} sent the following message: {user_message}"
                        print(f"New chat message: {formatted_message}")
                        
                        # Include player coordinates in the prompt
                        response = process_chat_with_gpt(client, GPT_MODEL, formatted_message, player_coords)
                        print(f"GPT Response: {response}")
                        handle_gpt_response(response)
            last_position = current_size
        time.sleep(1)

def execute_minecraft_command(command, optional_message=None):
    with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
        if command:
            execute_command = f"execute as {player_executor} at @s run {command}"
            print(f"Executing command as {player_executor}: /{execute_command}")
            mcr.command(f"/{execute_command}")
        if optional_message:
            tellraw_command = f'tellraw @a ["",{{"text":"[ChatGPT]: ","color":"gold"}},{{"text":"{optional_message}"}}]'
            print(f"Sending message with tellraw: {tellraw_command}")
            mcr.command(tellraw_command)



if __name__ == '__main__':
    server_file = download_minecraft_server(version='latest')
    if server_file:
        log_file_path = "./logs/latest.log"  # Adjust as necessary
        threading.Thread(target=setup_server, args=(server_file, True, './server.properties')).start()
        time.sleep(10)  # Give the server time to start; adjust as necessary
        monitor_chat_and_process_with_gpt(log_file_path, OPENAI_API_KEY)
