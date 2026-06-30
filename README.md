# Cooper Wake-Up Call

[![Support me on Patreon](https://img.shields.io/badge/Patreon-Support%20my%20work-FF424D?style=flat&logo=patreon&logoColor=white)](https://www.patreon.com/AndersBjarby)

A personal AI alarm clock that wakes you up in the voice of FBI Special Agent Dale Cooper from Twin Peaks. It gathers today's weather, news headlines and your calendar, has GPT-4 write an in-character wake-up monologue (complete with owls, pie and coffee references), turns it into speech with ElevenLabs, mixes it over the Twin Peaks theme, and plays it.

## What it does

- Fetches the weather for a location from `wttr.in`.
- Scrapes a news site and summarizes the top stories with the OpenAI API.
- Pulls today's events from iCloud Calendar over CalDAV.
- Generates a Dale Cooper-style wake-up call with GPT-4 and voices it via ElevenLabs.
- Fades in background music and overlays the spoken clip with `pydub`, then plays the result with `pygame`.

## Setup

Requires Python 3 and an OpenAI + ElevenLabs account. Install the dependencies:

```bash
pip install requests beautifulsoup4 caldav pytz openai elevenlabs pydub pygame python-dotenv
```

You'll need to fill in your own credentials (the script ships with placeholders):

- `OPENAI_API_KEY` (read from the environment / `.env`)
- Your ElevenLabs API key in `set_api_key(...)`
- Your iCloud email and an app-specific password (from https://appleid.apple.com/)
- A background music file (the script references `09 Dance Of The Dream Man.mp3`)

Then run:

```bash
python3 cooper.py
```

## Tech

Python, OpenAI GPT-4, ElevenLabs TTS, CalDAV (iCloud), wttr.in, BeautifulSoup, pydub, pygame.
