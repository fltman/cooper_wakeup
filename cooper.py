#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import caldav
from datetime import datetime, timedelta
import pytz
from openai import OpenAI
from elevenlabs import voices, generate, save, set_api_key
from pydub import AudioSegment
from math import log10
import pygame
import time
from dotenv import load_dotenv
load_dotenv()


set_api_key("xxxxxxxxxxx")

client = OpenAI()

def create_wakeup_call(filename, weather, news, calendar):
	voice_id = "lje26CmCiDS96gwa1RBG"
		
	messages= [
		{
			"role": "user",
			"content": "You are FBI special agent Dale Cooper from the tv series Twin Peaks. You like to make twin peak references to the owls, pie and coffee etc. Always reply in english."
		}
	]

	now = datetime.now()
	
	# Extract date, weekday, and time
	current_date = now.date()
	weekday = now.strftime("%A")  # This gives the full weekday name
	current_time = now.time()
	
	# Combine into a single variable (as a string for example)
	date_weekday_time = f"Date: {current_date}, Weekday: {weekday}, Time: {current_time}"
	
	messages.append(
		{
			"role": "user",
			"content": f"Stay in character and wake Anders up based on this:\n\n\
Date and time:{date_weekday_time}\n\n\
Todays weather:{weather}\n\n\
Todays Calendar:```{calendar}```\n\n\
Todays News:```{news}```	\n\n\
Don't forget to include the time, day, month and weekday, the weather and the news. Only reply with the wake up call."
		}
	)
	print (messages)
	response = client.chat.completions.create(
		model="gpt-4-1106-preview",
		messages=messages,
		temperature=1,
		top_p=1,
		frequency_penalty=0,
		presence_penalty=0
	)
	
	render_audio(filename, response.choices[0].message.content, voice_id)
	print (response.choices[0].message.content)
	return response.choices[0].message.content
	
def summarize_news(content):
	response = client.chat.completions.create(
		model="gpt-4-1106-preview",
		messages=[
			{
				"role": "user",
				"content": f"The content below is from extracting text from a webpage. Summarize the top news for me: \n\n{content}"
			}
		],
		temperature=1,
		max_tokens=256,
		top_p=1,
		frequency_penalty=0,
		presence_penalty=0
	)
	
	return response.choices[0].message.content

def render_audio(filepath, text, voice_id):
	audio = generate(text=text, voice=voice_id,
		model='eleven_multilingual_v2')
	save(audio, filepath)

def fetch_webpage_text(url):
	try:
		response = requests.get(url)
		response.raise_for_status()  # This will raise an exception for HTTP errors
		
		# Parse the content with BeautifulSoup
		soup = BeautifulSoup(response.content, 'html.parser')
		return soup.get_text(separator='\n', strip=True)
	except requests.RequestException as e:
		return str(e)

def get_weather(location):
	base_url = f"http://wttr.in/{location}?M"
	# Updated format string to include wind speed in m/s
	params = {
		'format': 'Location: %l\nWeather: %C\nTemperature: %t (feels like: %f)\nWind: %w\nPressure: %P\nHumidity: %h'
	}
	
	try:
		response = requests.get(base_url, params=params)
		response.raise_for_status()  # Raises an exception for HTTP errors
		
		return response.text.strip()
	except requests.RequestException as e:
		return str(e)

def get_todays_icloud_events(username, app_specific_password):
	# iCloud CalDAV URL
	url = 'https://caldav.icloud.com/'
	
	# Connect to the CalDAV server
	client = caldav.DAVClient(url, username=username, password=app_specific_password)
	principal = client.principal()
	calendars = principal.calendars()
	summary = ""
	if calendars:
		# Assuming you want to check the first calendar
		calendar = calendars[0]
		
		# Define the time range for today
		now = datetime.now(pytz.utc)
		start = datetime(now.year, now.month, now.day, tzinfo=pytz.utc)
		end = start + timedelta(days=1)
		
		# Fetch events for today
		events = calendar.date_search(start, end)
		
		for event in events:
			#print(event.instance.vevent.summary.value, event.instance.vevent.dtstart.value)
			summary = f"{summary}\n{event.instance.vevent.summary.value}, {event.instance.vevent.dtstart.value}"
		return summary
	
	else:
		print("No calendars found.")
		return []

def fade_audio_add_clip(main_file_path, additional_clip_path, start_fade_time, fade_duration, new_volume_percentage, overlay_start_time):
	# Load the main audio file
	audio = AudioSegment.from_mp3(main_file_path)
	
	# Load the additional audio clip
	additional_clip = AudioSegment.from_mp3(additional_clip_path)
	
	# Convert times to milliseconds
	start_fade_time_ms = start_fade_time * 1000
	fade_duration_ms = fade_duration * 1000
	overlay_start_time_ms = overlay_start_time * 1000
	
	# Split the audio into two parts
	before_fade = audio[:start_fade_time_ms]
	after_fade = audio[start_fade_time_ms:]
	
	# Calculate the target volume in dBFS
	target_volume_dbfs = audio.dBFS + 20 * log10(new_volume_percentage / 100)
	
	# Apply fade effect to the beginning of the after_fade section
	after_fade_start = after_fade[:fade_duration_ms].fade(to_gain=target_volume_dbfs, end=len(after_fade[:fade_duration_ms]), duration=fade_duration_ms)
	after_fade_remainder = after_fade[fade_duration_ms:]
	
	# Adjust the volume of the remainder of the after_fade section to match the target volume
	after_fade_remainder = after_fade_remainder - (after_fade_remainder.dBFS - target_volume_dbfs)
	
	# Combine the sections
	faded_audio = before_fade + after_fade_start + after_fade_remainder
	
	# Overlay the additional clip at 32 seconds
	combined_audio = faded_audio.overlay(additional_clip, position=overlay_start_time_ms)
	
	# Save the modified audio to a new file
	combined_audio.export("combined_audio_twinpeaks.mp3", format="mp3")
	
def play_mp3(file_path):
	# Initialize pygame mixer
	pygame.mixer.init()
	
	# Load the MP3 file
	pygame.mixer.music.load(file_path)
	
	# Start playing the MP3 file
	pygame.mixwinr.music.play()
	
	# Wait for the music to finish playing
	while pygame.mixer.music.get_busy():
		time.sleep(1)
		

#print (calendar)
url = "http://dn.se"
location = "Kalmar"
news = summarize_news(fetch_webpage_text(url))
weather = get_weather(location)
calendar = get_todays_icloud_events('anders@xxxxxxxx.com', 'xxxxxxxxXXXXxx')	#https://appleid.apple.com/


current_timestamp = datetime.now()

# Format the timestamp as 'YYYYMMDD_hhmmss'
formatted_timestamp = current_timestamp.strftime("%Y%m%d_%H%M%S")

# Append .mp3 extension
filename = f"{formatted_timestamp}.mp3"

create_wakeup_call(filename, weather, news, calendar)

# Use the function on your audio files
fade_audio_add_clip("09 Dance Of The Dream Man.mp3", filename, 28, 5, 5, 32)
#
play_mp3('combined_audio_twinpeaks.mp3')
