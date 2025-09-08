import time
import vosk
import pyttsx3
import asyncio
import json
import sounddevice as sd
import numpy as np
import wave
from word2number import w2n  # Converts spoken words into numbers

# Load Vosk model
model = vosk.Model("vosk_model")  # Ensure the vosk_model folder is in your directory
rec = vosk.KaldiRecognizer(model, 16000)

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)  # Adjust speech speed

# Store executed commands
executed_commands = []

# Default values
DEFAULT_TURN_SPEED = 50
DEFAULT_MIN_SPEED=1
DEFAULT_MOVE_SPEED = 500
DEFAULT_MIN_TIMEOUT = 1
DEFAULT_TIMEOUT = 3
DEFAULT_AUDIO_TIMEOUT = 5  # Default timeout for voice input

def speak(text):
    """Convert text to speech and wait for completion."""
    engine.say(text)
    engine.runAndWait()

def record_audio(duration=DEFAULT_AUDIO_TIMEOUT, filename="input.wav"):
    """Records audio for speech recognition."""
    fs = 16000  # Sample rate
    print(f"🎤 Recording for {duration} seconds...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype=np.int16)
    sd.wait()

    wavefile = wave.open(filename, 'wb')
    wavefile.setnchannels(1)
    wavefile.setsampwidth(2)
    wavefile.setframerate(fs)
    wavefile.writeframes(audio.tobytes())
    wavefile.close()

    return filename

def transcribe_audio(filename="input.wav"):
    """Uses Vosk to transcribe recorded audio."""
    with wave.open(filename, "rb") as wf:
        data = wf.readframes(wf.getnframes())
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "").strip().lower()
            print(f"🗣 You said: {text}")
            return text
    return ""
def get_valid_number_required(prompt, min_value=None, max_value=None):
    """Requires the user to provide a value (no default allowed)."""
    speak(prompt)

    while True:
        filename = record_audio(duration=DEFAULT_AUDIO_TIMEOUT)
        spoken_text = transcribe_audio(filename)

        if spoken_text:
            try:
                number = w2n.word_to_num(spoken_text)
                if min_value is not None and max_value is not None:
                    if min_value <= number <= max_value:
                        speak(f"You said {number}.")
                        return number
                    else:
                        speak(f"Please provide a number between {min_value} and {max_value}.")
                else:
                    speak(f"You said {number}.")
                    return number
            except ValueError:
                speak("That doesn't seem like a valid number. Try again.")

def get_valid_number(prompt, min_value=None, max_value=None, default_value=None):
    """Ask for a valid number, allowing 'default' for all parameters."""
    speak(f"{prompt} or say 'default' to use {default_value}.")

    while True:
        filename = record_audio(duration=DEFAULT_AUDIO_TIMEOUT)
        spoken_text = transcribe_audio(filename)

        if spoken_text:
            if "default" in spoken_text and default_value is not None:
                speak(f"Using default value: {default_value}.")
                return default_value

            try:
                number = w2n.word_to_num(spoken_text)  # Convert words like "one thousand" → 1000
                if min_value is not None and max_value is not None:
                    if min_value <= number <= max_value:
                        speak(f"You said {number}.")
                        return number
                    else:
                        speak(f"Please provide a number between {min_value} and {max_value}.")
                else:
                    speak(f"You said {number}.")
                    return number
            except ValueError:
                speak("That doesn't seem like a valid number. Try again.")

def get_confirmation(prompt):
    """Keep asking until the user gives a valid yes/no response."""
    while True:
        speak(prompt)
        filename = record_audio(duration=DEFAULT_AUDIO_TIMEOUT)
        response = transcribe_audio(filename)

        if response:
            if "yes" in response:
                return True
            elif "no" in response:
                return False
            else:
                speak("Please say yes or no.")

async def my_distance_with_tank_cm_time(distance: int, speed: int, maxtime: int):
    """Move forward a given distance at a certain speed and time."""
    command_str = f"✅ await my_distance_with_tank_cm_time({distance}, {speed}, {maxtime})"
    executed_commands.append(command_str)
    speak(f"Moving forward {distance} centimeters at speed {speed} for {maxtime} milliseconds.")
    await asyncio.sleep(maxtime / 1000)
    print(command_str)

async def my_distance_with_tank_cm_time_back(distance: int, speed: int, maxtime: int):
    """Move back a given distance at a certain speed and time (negative speed)."""
    command_str = f"✅ await my_distance_with_tank_cm_time({distance}, {-speed}, {maxtime})"
    executed_commands.append(command_str)
    speak(f"Moving back {distance} centimeters at speed {speed} for {maxtime} milliseconds.")
    await asyncio.sleep(maxtime / 1000)
    print(command_str)

async def turn_with_gyro_left(angle: float, speed: int, maxtime: int):
    """Turn left to a specified angle at a certain speed, limited by time."""
    command_str = f"✅ await turn_with_gyro_left({angle}, {speed}, {maxtime})"
    executed_commands.append(command_str)
    speak(f"Turning left {angle} degrees at speed {speed} for {maxtime} milliseconds.")
    await asyncio.sleep(maxtime / 1000)
    print(command_str)

async def turn_with_gyro_right(angle: float, speed: int, maxtime: int):
    """Turn right to a specified angle at a certain speed, limited by time (negative angle)."""
    angle = -abs(angle)  # Ensure the angle is negative
    command_str = f"✅ await turn_with_gyro_right({angle}, {speed}, {maxtime})"
    executed_commands.append(command_str)
    speak(f"Turning right {angle} degrees at speed {speed} for {maxtime} milliseconds.")
    await asyncio.sleep(maxtime / 1000)
    print(command_str)

def ask_for_comment():
    """Ask user if they want to add a comment."""
    speak("Would you like to add a comment? Say yes or no.")
    filename = record_audio(duration=DEFAULT_AUDIO_TIMEOUT)
    response = transcribe_audio(filename)

    if "yes" in response:
        speak("Please say your comment.")
        filename = record_audio(duration=DEFAULT_AUDIO_TIMEOUT)
        comment = transcribe_audio(filename)
        if comment:
            return f"# {comment}"

    return ""

async def main():
    speak("Welcome to the Voice-Controlled Movement Program.")

    while True:
        startTime = time.time()
        speak("Say Move forward, Move back, Turn left, Turn right, say command with defaults for default values, Help, or Exit.")
        filename = record_audio(duration=DEFAULT_AUDIO_TIMEOUT)
        command = transcribe_audio(filename)

        if command:
            if "move forward with defaults" in command:
                            distance = get_valid_number_required("Say the distance in centimeters.")



                            if get_confirmation(f"Confirm: Move forward {distance} centimeters at {speed} speed for {time_in_seconds} seconds. Say yes to continue."):
                                command_str = f"await my_distance_with_tank_cm_time({distance}, {speed}, {maxtime})"
                                comment = ask_for_comment()
                                executed_commands.append(command_str)
                                executed_commands.append(comment)
            elif "move forward" in command:
                distance = get_valid_number_required("Say the distance in centimeters.")
                speed = get_valid_number("Say the speed in rotations per second.", DEFAULT_MIN_SPEED, default_value=DEFAULT_MOVE_SPEED)
                time_in_seconds = get_valid_number("Say the maximum time in seconds.", DEFAULT_MIN_TIMEOUT, default_value=DEFAULT_TIMEOUT)
                maxtime = time_in_seconds * 1000

                if get_confirmation(f"Confirm: Move forward {distance} centimeters at {speed} speed for {time_in_seconds} seconds. Say yes to continue."):
                    command_str = f"await my_distance_with_tank_cm_time({distance}, {speed}, {maxtime})"
                    comment = ask_for_comment()
                    executed_commands.append(command_str)

                    executed_commands.append(comment)

            elif "move back with defaults" in command:
                distance = get_valid_number_required("Say the distance in centimeters.")
                speed = DEFAULT_MOVE_SPEED
                time_in_seconds = DEFAULT_TIMEOUT
                maxtime = time_in_seconds * 1000

                if get_confirmation(f"Confirm: Move back {distance} centimeters at {speed} speed for {time_in_seconds} seconds. Say yes to continue."):
                    command_str = f"await my_distance_with_tank_cm_time({distance}, {-speed}, {maxtime})"
                    comment = ask_for_comment()
                    executed_commands.append(command_str)
                    executed_commands.append(comment)

            elif "move back" in command:
                distance = get_valid_number_required("Say the distance in centimeters.")
                speed = get_valid_number("Say the speed in rotations per second.", DEFAULT_MIN_SPEED, default_value=DEFAULT_MOVE_SPEED)
                time_in_seconds = get_valid_number("Say the maximum time in seconds.", DEFAULT_MIN_TIMEOUT, default_value=DEFAULT_TIMEOUT)
                maxtime = time_in_seconds * 1000

                if get_confirmation(f"Confirm: Move back {distance} centimeters at {speed} speed for {time_in_seconds} seconds. Say yes to continue."):
                    command_str = f"await my_distance_with_tank_cm_time({distance}, {-speed}, {maxtime})"
                    comment = ask_for_comment()
                    executed_commands.append(command_str)
                    executed_commands.append(comment)

            elif command == "turn left with defaults":
                angle = get_valid_number_required("Say the turning angle in degrees.", min_value=0, max_value=180)
                speed = DEFAULT_TURN_SPEED
                time_in_seconds = DEFAULT_TIMEOUT
                maxtime = time_in_seconds * 1000

                if get_confirmation(f"Confirm: Turn left {angle} degrees at {speed} speed for {time_in_seconds} seconds. Say yes to continue."):
                    command_str = f"await turn_with_gyro_left({angle}, {speed}, {maxtime})"
                    comment = ask_for_comment()
                    executed_commands.append(command_str)
                    executed_commands.append(comment)

            elif command == "turn left":
                angle = get_valid_number_required("Say the turning angle in degrees.", min_value=0, max_value=180)
                speed = get_valid_number("Say the turning speed in rotations per second, or say 'default' to use 50.", DEFAULT_MIN_SPEED, default_value=DEFAULT_TURN_SPEED)
                time_in_seconds = get_valid_number("Say the maximum time in seconds, or say 'default' to use 3.", DEFAULT_MIN_TIMEOUT, default_value=DEFAULT_TIMEOUT)
                maxtime = time_in_seconds * 1000

                if get_confirmation(f"Confirm: Turn left {angle} degrees at {speed} speed for {time_in_seconds} seconds. Say yes to continue."):
                    command_str = f"await turn_with_gyro_left({angle}, {speed}, {maxtime})"
                    comment = ask_for_comment()
                    executed_commands.append(command_str)
                    executed_commands.append(comment)

            elif command == "turn right with defaults":
                angle = get_valid_number_required("Say the turning angle in degrees.", min_value=0, max_value=180)
                speed = DEFAULT_TURN_SPEED
                time_in_seconds = DEFAULT_TIMEOUT
                maxtime = time_in_seconds * 1000

                if get_confirmation(f"Confirm: Turn right {angle} degrees at {speed} speed for {time_in_seconds} seconds. Say yes to continue."):
                     command_str = f"await turn_with_gyro_right({-angle}, {speed}, {maxtime})"
                     comment = ask_for_comment()
                     executed_commands.append(command_str)
                     executed_commands.append(comment)

            elif command == "turn right":
                angle = get_valid_number_required("Say the turning angle in degrees.", min_value=0, max_value=180)
                speed = get_valid_number("Say the turning speed in rotations per second, or say 'default' to use 50.", DEFAULT_MIN_SPEED, default_value=DEFAULT_TURN_SPEED)
                time_in_seconds = get_valid_number("Say the maximum time in seconds, or say 'default' to use 3.", DEFAULT_MIN_TIMEOUT, default_value=DEFAULT_TIMEOUT)
                maxtime = time_in_seconds * 1000


                if get_confirmation(f"Confirm: Turn right {angle} degrees at {speed} speed for {time_in_seconds} seconds. Say yes to continue."):
                     command_str = f"await turn_with_gyro_right({-angle}, {speed}, {maxtime})"
                     comment = ask_for_comment()
                     executed_commands.append(command_str)
                     executed_commands.append(comment)

            elif "exit" in command:
                speak("Goodbye! Printing all executed commands before exiting.")
                print("\n📜 **Executed Commands Summary:**")
                for cmd in executed_commands:
                    print(cmd)
                break

            else:
                speak("I did not recognize that command. Please try again.")

            totalTime = time.time() - startTime
            print("\n Command Processing time {} : {}.".format(command_str, totalTime))

if __name__ == "__main__":
    asyncio.run(main())
