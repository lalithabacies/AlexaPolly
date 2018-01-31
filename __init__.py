"""Getting Started Example for Python 2.7+/3.3+"""
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from flask import Flask,request
import requests
import boto3
import simplejson as json
from googletrans import Translator


app=Flask(__name__)
app.secret_key = "amazon_polly_0343sdsad@#$#$%vb2u2"

aws_access_key_id = "AKIAIXQSPFFFCBPHBAHQ"
aws_secret_access_key = "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"
region_name="us-west-2" 
s3 = boto3.client('s3',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
# Create a client using the credentials and region defined in the [adminuser]
# section of the AWS credentials file (~/.aws/credentials).
session = Session(profile_name="adminuser")
polly = session.client("polly") 

@app.route('/',methods=['GET','POST'])
def homepage():      
    pass
@app.route('/get_text',methods=['GET','POST'])
def get_text(lang='en'):
    result = requests.get('https://lighthouse247.com//shared_services/babel/babel_test.php?case=1').json()
    if 'source' in result:
        Text_URL = result['source']
        Text_content = requests.get(Text_URL).text
        if 'lang' in request.args:
            lang = request.args.get('lang')
            if lang == 'en':
                return Text_content
            else:
                if 'trans_tool' in request.args:
                    trans_tool = request.args.get('trans_tool')
                    if trans_tool == 'google':
                        translator = Translator()
                        translation = translator.translate(Text_content, dest='es')
                        Text_content = translation.text
                        return Text_content
                    else: 
                        ##amazon translator
                        pass
                else:
                    translator = Translator()
                    translation = translator.translate(Text_content, dest='es')
                    Text_content = translation.text
                    return Text_content
        else:
            return Text_content
            
@app.route('/get_shortaudio',methods=['GET','POST'])
def get_shortaudio(lang='en'):
    if 'lang' in request.args:
        lang = request.args.get('lang')
    else:
        lang = 'en'
        
    split_string = lambda x, n: [x[i:i+n] for i in range(0, len(x), n)]
    splitted_text = split_string(str(get_text(lang)),1000)
    sounds       = []
    for l in range(0,len(splitted_text)):
        # Request speech synthesis
        response = polly.synthesize_speech(Text=str(splitted_text[l]), OutputFormat="mp3", VoiceId="Joey")
        
        if "AudioStream" in response:
            # Note: Closing the stream is important as the service throttles on the
            # number of parallel connections. Here we are using contextlib.closing to
            # ensure the close method of the stream object will be called automatically
            # at the end of the with statement's scope.
            with closing(response["AudioStream"]) as stream:
                #print(gettempdir())
                #output = os.path.join(gettempdir(), "speech.mp3")
                output = "speech"+str(l)+".mp3"

                try:
                    # Open a file for writing the output as a binary stream
                    with open(output, "wb") as file:
                        file.write(stream.read())
                    bucket_name = 'amazon-polly'
                    filename    = output
                    s3.upload_file(filename, bucket_name, filename,
                        ExtraArgs={'ACL': 'public-read'}
                    )
                    s3_url = 'https://s3-us-west-2.amazonaws.com/%s/%s' % (bucket_name, filename)
                    sounds.append(s3_url)
                except IOError as error:
                    # Could not write to file, exit gracefully
                    print(error)
                    #sys.exit(-1)                       
        else:
            # The response didn't contain audio data, exit gracefully
            print("Could not stream audio")
            #sys.exit(-1)
    return sounds            
            
@app.route('/get_longaudio',methods=['GET','POST'])
def get_longaudio(lang='en'):
    short_audio_urls = get_shortaudio(lang)
    r = requests.post('http://localhost/AmazonPolly_mp3merge_api/index.php', json = {'Files_To_Merge':short_audio_urls},headers={'Content-type': 'application/json'})
    combined_url = r.json()['combined_mp3']      
    return combined_url
                


if __name__ == '__main__':
    #app.run(debug = True)
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)