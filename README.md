# Custom Sound Bot
A Discord bot that plays custom sounds when users join or leave voice channels, with sound imports from Tuna.

## Description
CustomSoundBot enhances your server with personalized sound effects. Assign unique sounds to members, import MP3s from Tuna, and enjoy seamless voice channel integration. Perfect for fun and utility!

## Prerequisites
- Python 3.8 or higher
- FFmpeg installed (e.g., `brew install ffmpeg` on macOS, `sudo apt install ffmpeg` on Linux, or download from https://ffmpeg.org for Windows)

## Setup
1. **Download**: Clone or download this folder.
2. **Install Dependencies**: Run `pip install -r requirements.txt` in the project directory.
3. **Install FFmpeg**: Ensure FFmpeg is in your system PATH.
4. **Configure Environment**:
   - Copy `.env.example` to `.env`.
   - Add your Discord bot token (`DISCORD_TOKEN`) from https://discord.com/developers/applications.
   - Optionally, add a Tuna API token (`TUNA_TOKEN`) if available.
5. **Run the Bot**: Execute `python bot.py`.
6. **Invite the Bot**: Use the invite URL logged on startup (requires connect, speak, read/send messages, and manage messages permissions).

## Commands
- `/adduser`: Add a server member to the sound map with a custom sound (admin only).
- `/tunalogin`: Get a link to log into Tuna for enhanced sound searches (admin only).
- `/tunacode <code>`: Submit a Tuna authorization code (admin only).
- `/importsound <query>`: Search Tuna for MP3s, preview them, and import one (admin only).

## Notes
- **Sound Files**: Can be stored anywhere accessible on your system; `sounds/` is used for Tuna imports by default.
- **Previews**: You must be in a voice channel to hear sound previews with `/importsound`.
- **App Directory**: Find us in the Discord App Directory under tags: Sound, Voice, Fun, Utility, Music.

## Privacy Policy
We collect Discord member IDs and sound file paths, stored locally in `config.json`. Data is not shared except with Tuna (optional, for imports). See [Privacy Policy](https://yourname.github.io/privacy) for details.

## Terms of Service
Do not upload illegal or age-restricted content. See [Terms of Service](https://yourname.github.io/tos) for full terms.

## Support
Join our support server: [insert invite link] or email [your-email].