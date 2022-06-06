import requests, os, uuid, json
from dotenv import load_dotenv
load_dotenv()
import azure.cognitiveservices.speech as speechsdk


from flask import Flask, request, render_template

app = Flask(__name__,template_folder='templates')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def index_post():
    # Read the values from the form
    original_text = request.form['text']
    target_language = request.form['language']


    #print(target_language)
    speech_config = speechsdk.SpeechConfig(subscription=os.environ['KEY_1'], region=os.environ['REGION'])
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

# The language of the voice that speaks.
    if(target_language == "hi"):
        speech_config.speech_synthesis_voice_name='hi-IN-SwaraNeural'
    elif(target_language == "it"):
        speech_config.speech_synthesis_voice_name='it-IT-IsabellaNeural'
    elif(target_language == "ko"):
        speech_config.speech_synthesis_voice_name='ko-KR-SunHiNeural'
    elif(target_language == "de"):
        speech_config.speech_synthesis_voice_name='de-DE-KatjaNeural'
    else:
        speech_config.speech_synthesis_voice_name='en-US-SaraNeural'

    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    # Load the values from .env
    key = os.environ['KEY']
    endpoint = os.environ['ENDPOINT']
    location = os.environ['REGION']

    # Indicate that we want to translate and the API version (3.0) and the target language
    path = '/translate?api-version=3.0'
    # Add the target language parameter
    target_language_parameter = '&to=' + target_language
    # Create the full URL
    constructed_url = endpoint + path + target_language_parameter

    # Set up the header information, which includes our subscription key
    headers = {
        'Ocp-Apim-Subscription-Key': key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # Create the body of the request with the text to be translated
    body = [{ 'text': original_text }]

    # Make the call using post
    translator_request = requests.post(constructed_url, headers=headers, json=body)
    # Retrieve the JSON response
    translator_response = translator_request.json()
    # Retrieve the translation
    translated_text = translator_response[0]['translations'][0]['text']

    text = translated_text

    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

   
    # Call render template, passing the translated text,
    # original text, and target language to the template
    return render_template(
        'result.html',
        translated_text=translated_text,
        original_text=original_text,
        target_language=target_language
    )

    

if __name__ == "__main__":
    app.run(debug=True)