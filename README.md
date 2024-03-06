# GPT-4 Minecraft Command Integration

This project integrates OpenAI's GPT-4 with Minecraft, enabling the execution of in-game commands through natural language processing. Our Python script bridges the gap, allowing for an innovative way to interact with Minecraft servers directly through GPT-4's advanced understanding of commands and chat inputs.

## Features

- Automatic downloading of the Minecraft server (latest version or specified version).
- Setup of the Minecraft server with RCON enabled for remote command execution.
- Real-time chat monitoring in Minecraft, processing messages through GPT-4.
- Execution of Minecraft commands based on GPT-4 responses, including custom messages and command execution as a specific player.

## Prerequisites

Before you begin, ensure you have the following installed:
- JDK 17: Required for running the Minecraft server. Download [here](https://www.oracle.com/java/technologies/javase/jdk17-archive-downloads.html).
- Python 3.8 or newer.

## Installation

Follow these steps to get the script up and running:

1. **Clone the repository:**
   ```
   git clone https://github.com/WilleDCrazy/MinecraftChatGPT/
   ```

2. **Install required Python packages:**
   ```
   pip install requests mcrcon openai
   ```

3. **Configuration:**
   - Open the Python script in your favorite editor.
   - Locate the `OPENAI_API_KEY` variable and insert your OpenAI API key.
   - (Optional) Adjust the `RCON_HOST`, `RCON_PORT`, and `RCON_PASSWORD` as needed to match your Minecraft server's configuration.
   - (Optional) Change `player_executor` to the Minecraft username that will be used for command execution.

4. **Starting the Minecraft server:**
   - Run the Python script. It will automatically download the Minecraft server jar file (if not present) and start the server with the appropriate settings for RCON:
     ```
     python Minecraft.py
     ```

## Usage

With the script running and the Minecraft server up:
- Any chat messages sent in-game will be intercepted by the script.
- The script processes these messages through GPT-4 to determine appropriate Minecraft commands or chat responses.
- Commands are executed on the server as the specified player, and responses are sent back into the game chat.

## Contributing

We welcome contributions and suggestions! Feel free to fork the repository, make changes, and submit pull requests.

## License

MIT License

Credit me if you decide to use my code for content creation, please.

## Acknowledgments

- OpenAI for the GPT-4 API.
- The Minecraft community for the inspiration and support.
