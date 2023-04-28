import speech_recognition as sr
import requests
import random
import time
import os


def check_status(inference_job_token: str):
    url = f"https://api.fakeyou.com/tts/job/{inference_job_token}"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    r = requests.get(url, headers=headers)

    return [r.json()["state"]["status"], r.json()["state"]["maybe_public_bucket_wav_audio_path"]]


def generate_random_token():
    # Generate a random token
    letters = "abcdefghijklmnopqrstuvwxyz0123456789[]{}"
    token = ""

    for _ in range(0, 30):
        token += random.choice(letters)

    print("Token: " + token)

    return token


def say(text):
    # Use FakeYou's API to convert text to speech
    voice_modal_token = "TM:43c7p13p3z5c"
    token = generate_random_token()

    data = {
        "uuid_idempotency_token": token,
        "tts_model_token": voice_modal_token,
        "inference_text": text,
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    r = requests.post(
        "https://api.fakeyou.com/tts/inference", json=data, headers=headers)

    print(r.text)

    job_token = r.json()["inference_job_token"]

    # Wait for 10 seconds
    time.sleep(10)

    # Check the status of the inference job
    status = ""
    public_url = ""

    while status != "complete_success":
        if status in ["complete_failure", "attempt_failed", "dead"]:
            print("Failed to convert text to speech.")
            break

        status, public_url = check_status(job_token)
        time.sleep(10)
        print("Status: " + status)

    # Download the audio file
    url = f"https://storage.googleapis.com/vocodes-public/{public_url}"

    print("Available at: " + public_url)
    print("Raw: " + url)
    r2 = requests.get(url)

    with open("audio.wav", "wb") as f:
        f.write(r2.content)

    # Play the audio file
    os.system("audio.wav")


def main():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Speak now:")
        audio = r.listen(source)

    try:
        response_text = r.recognize_google(audio)

        say(response_text)

    except sr.UnknownValueError:
        say("Sorry, I could not understand what you said.")
    except sr.RequestError as e:
        say(
            "Could not request results from Google Speech Recognition service; {0}".format(e))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
