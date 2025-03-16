# Custom Sound Bot
A Discord bot that plays custom sounds when users join or leave voice channels, with sound imports from Tuna.

## Description
CustomSoundBot enhances your server with personalized sound effects. Assign unique sounds to members, import MP3s from Tuna, and enjoy seamless voice channel integration. Perfect for fun and utility!

## Installation via Discord App Directory
1. **Add the Bot**:
   - Find "CustomSoundBot" in the Discord App Directory (under tags: Sound, Voice, Fun, Utility, Music).
   - Click "Add to Server" and follow the prompts to invite the bot to your server.
2. **Download the Bot Files**:
   - Download the latest release from the link provided in the App Directory or support server: [insert download link, e.g., Google Drive/Dropbox].
   - Alternatively, clone the source code from GitHub (optional): [insert GitHub repo URL].
3. **Set Up Locally**:
   - Unzip the downloaded `CustomSoundBot.zip`.
   - Install Python 3.8+ and FFmpeg (e.g., `brew install ffmpeg` on macOS, `sudo apt install ffmpeg` on Linux, or download from https://ffmpeg.org for Windows).
   - Install dependencies: `pip install -r requirements.txt`.
   - Copy `.env.example` to `.env` and add your `DISCORD_TOKEN` (from the Discord Developer Portal: https://discord.com/developers/applications).
   - Optionally, add a `TUNA_TOKEN` if using authenticated Tuna searches.
   - Run the bot: `python bot.py`.
4. **Verify Installation**:
   - The bot should log an invite URL (already added via App Directory) and sync slash commands.
   - Use `/adduser` or `/importsound` to test functionality.

## Commands
- `/adduser`: Add a member to the sound map with a custom sound (admin only).
- `/tunalogin`: Get a link to log into Tuna for enhanced sound searches (admin only).
- `/tunacode <code>`: Submit a Tuna authorization code (admin only).
- `/importsound <query>`: Search Tuna for MP3s, preview them, and import one (admin only).

## Notes
- **Local Hosting**: This bot runs locally on your machine. Keep it running to ensure functionality.
- **Sound Files**: Can be stored anywhere accessible; `sounds/` is used for Tuna imports by default.
- **Previews**: You must be in a voice channel to hear sound previews with `/importsound`.
- **GitHub Repository**: For source code and contributions, visit [insert GitHub repo URL].

## Privacy Policy
We collect Discord member IDs and sound file paths, stored locally in `config.json`. Data is not shared except with Tuna (optional, for imports). See [Privacy Policy](https://yourname.github.io/privacy) for details.

## Terms of Service
Do not upload illegal or age-restricted content. See [Terms of Service](https://yourname.github.io/tos) for full terms.

## Support
Join our support server: [insert invite link] or email [your-email].