"""Getting Started Example for Python 2.7+/3.3+"""
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir
from flask import Flask,request
import requests

app=Flask(__name__)
app.secret_key = "amazon_polly_0343sdsad@#$#$%vb2u2"

# Create a client using the credentials and region defined in the [adminuser]
# section of the AWS credentials file (~/.aws/credentials).
session = Session(profile_name="adminuser")
polly = session.client("polly")

try:
    result = requests.get('https://lighthouse247.com//shared_services/babel/babel_test.php?case=1').json()
    print(str(result))
    text = 'hi'
    # Request speech synthesis
    response = polly.synthesize_speech(Text=text, OutputFormat="mp3", VoiceId="Joey")
except (BotoCoreError, ClientError) as error:
    # The service returned an error, exit gracefully
    print(error)
    sys.exit(-1)

# Access the audio stream from the response
if "AudioStream" in response:
    # Note: Closing the stream is important as the service throttles on the
    # number of parallel connections. Here we are using contextlib.closing to
    # ensure the close method of the stream object will be called automatically
    # at the end of the with statement's scope.
    with closing(response["AudioStream"]) as stream:
        #print(gettempdir())
        #output = os.path.join(gettempdir(), "speech.mp3")
        output = "speech.mp3"

        try:
            # Open a file for writing the output as a binary stream
            with open(output, "wb") as file:
                file.write(stream.read())
        except IOError as error:
            # Could not write to file, exit gracefully
            print(error)
            sys.exit(-1)

else:
    # The response didn't contain audio data, exit gracefully
    print("Could not stream audio")
    sys.exit(-1)

# Play the audio using the platform's default player
# if sys.platform == "win32":
    # os.startfile(output)
# else:
    # # the following works on Mac and Linux. (Darwin = mac, xdg-open = linux).
    # opener = "open" if sys.platform == "darwin" else "xdg-open"
    # subprocess.call([opener, output])
    
if __name__ == '__main__':
    #app.run(debug = True)
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)