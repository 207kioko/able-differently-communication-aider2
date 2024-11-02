import speech_recognition as sr  # Ensure this is imported if you want to use it for microphone input
import pyttsx3
import os
import time
import requests
import json

# Define VLC paths explicitly
vlc_dll_path = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\VideoLAN "  # Ensure this path matches your VLC installation

try:
    import vlc  # Import VLC after setting up paths
except FileNotFoundError as e:
    print(f"Could not find VLC library: {e}")
    print("Ensure the VLC path is correct and VLC is installed.")
    exit(1)  # Exit if VLC library is not found

# Initialize Text-to-Speech engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)  # Adjust speech rate as needed

# Define video paths for sign language
sign_language_videos = {
    "hello": "C:/Users/Presentation/Desktop/Personal Projects/sign_language_videos/hello.mp4",
    "world": "C:/Users/Presentation/Desktop/Personal Projects/sign_language_videos/world.mp4",
    # Add other video paths as needed
}

def recognize_speech_assemblyai():
    """Converts spoken language to text using AssemblyAI."""
    print("Please speak now...")

    # Create a recognizer instance
    recognizer = sr.Recognizer()
    
    # Capture audio from the microphone
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
        audio_data = audio.get_wav_data()

    # Save the audio data to a temporary file
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_data)

    # Send audio file to AssemblyAI for transcription
    headers = {
        "authorization": "b81cda570df34c388d3e8ad43ac76d36",  # Replace with your API key
        "content-type": "application/json"
    }

    # Upload audio file to AssemblyAI
    upload_url = "https://api.assemblyai.com/v2/upload"
    with open("temp_audio.wav", "rb") as f:
        upload_response = requests.post(upload_url, headers=headers, data=f)

    # Check if upload was successful
    if upload_response.status_code != 200:
        print(f"Upload failed: {upload_response.status_code}")
        print(upload_response.text)  # Print the response text for debugging
        return None

    try:
        audio_url = upload_response.json().get('upload_url')
        if not audio_url:
            print("No audio URL returned from AssemblyAI.")
            return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from upload response: {e}")
        return None

    # Request transcription
    transcription_request = {
        "audio_url": audio_url
    }
    transcription_response = requests.post("https://api.assemblyai.com/v2/transcript", json=transcription_request, headers=headers)
    
    if transcription_response.status_code != 200:
        print(f"Transcription request failed: {transcription_response.status_code}")
        print(transcription_response.text)
        return None

    transcription_id = transcription_response.json().get('id')
    if not transcription_id:
        print("No transcription ID returned.")
        return None

    # Poll for the transcription result
    while True:
        polling_response = requests.get(f"https://api.assemblyai.com/v2/transcript/{transcription_id}", headers=headers)
        
        if polling_response.status_code != 200:
            print(f"Polling failed: {polling_response.status_code}")
            print(polling_response.text)
            return None

        polling_result = polling_response.json()
        
        if polling_result.get('status') == 'completed':
            return polling_result.get('text')
        elif polling_result.get('status') == 'failed':
            print("Transcription failed.")
            return None
        time.sleep(5)  # Wait before polling again

def play_sign_language(video_path):
    """Plays sign language video using VLC."""
    instance = vlc.Instance()  # Specify VLC plugin path if needed
    player = instance.media_player_new()
    media = instance.media_new(video_path)
    player.set_media(media)
    
    player.play()
    print(f"Playing sign language video for path: {video_path}")

    time.sleep(1)  # Allow time for VLC to load and start playing
    while player.is_playing():
        time.sleep(0.1)

    player.stop()  # Stop the player when video is finished

def translate_to_sign_language(text):
    """Translates text to sign language by playing videos for each word."""
    words = text.split()
    for word in words:
        word = word.lower()
        if word in sign_language_videos:
            video_path = sign_language_videos[word]
            print(f"Playing sign language for '{word}'")
            play_sign_language(video_path)
        else:
            print(f"No sign language video found for word: '{word}'")

def text_to_speech(text):
    """Converts text to speech for visually impaired users."""
    print(f"Converting text to speech: {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()

if __name__ == "__main__":
    recognized_text = recognize_speech_assemblyai()  # Capture spoken input using AssemblyAI

    if recognized_text:
        # Show text output for hearing-impaired users
        print(f"Displaying text: {recognized_text}")

        # Translate to sign language
        translate_to_sign_language(recognized_text)

        # Convert to audio for visually impaired users
        text_to_speech(recognized_text)
