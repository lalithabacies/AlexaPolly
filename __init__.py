# init.py file
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
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import time
import threading
from threading import Thread

app=Flask(__name__)
app.secret_key = "amazon_polly_0343sdsad@#$#$%vb2u2"

aws_access_key_id = "AKIAIXQSPFFFCBPHBAHQ"
aws_secret_access_key = "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"
region_name="us-west-2" 

s3 = boto3.client('s3',aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
# Create a client using the credentials and region defined in the [adminuser]
# section of the AWS credentials file (~/.aws/credentials).
session = Session(aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key,region_name=region_name)
polly = session.client("polly")
    
@app.route('/',methods=['GET','POST'])
def homepage():      
    return ''

@app.route('/gettext',methods=['GET','POST'])
def gettext():
    result = requests.get('https://lighthouse247.com//shared_services/babel/babel_test.php?case=1').json()
    Text_content = ''
    if 'source' in result:
        Text_URL = result['source']
        Text_content = requests.get(Text_URL).text
    return Text_content             
        
@app.route('/getshortaudio',methods=['GET','POST'])
def getshortaudio():
    result = requests.get('https://lighthouse247.com//shared_services/babel/babel_test.php?case=2').json()
    ShortAudio_URL = ''
    if 'source' in result:
        ShortAudio_URL = result['source']
    return ShortAudio_URL

@app.route('/getlongaudio',methods=['GET','POST'])
def getlongaudio():
    result = requests.get('https://lighthouse247.com//shared_services/babel/babel_test.php?case=3').json()
    LongAudio_URL = ''
    if 'source' in result:
        LongAudio_URL = result['source']
    return LongAudio_URL

@app.route('/getshortaudiopolly',methods=['GET','POST']) 
def getshortaudiopolly():
    result = requests.get('https://lighthouse247.com//shared_services/babel/babel_test.php?case=4').json()
    Text_content = ''
    if 'source' in result:
        Text_URL = result['source']
        Text_content = requests.get(Text_URL).text
    return getpollyaudio(Text_content,'short')

@app.route('/getlongaudiopolly',methods=['GET','POST']) 
def getlongaudiopolly():
    result = requests.get('https://lighthouse247.com//shared_services/babel/babel_test.php?case=5').json()
    Text_content = ''
    if 'source' in result:
        Text_URL = result['source']
        Text_content = requests.get(Text_URL).text
    return getpollyaudio(Text_content,'long')  

@app.route('/get_googletranslate_polly',methods=['GET','POST']) 
def get_googletranslate_polly():
    result = requests.get('https://lighthouse247.com//shared_services/babel/babel_test.php?case=6').json()
    Text_content = ''
    if 'source' in result:
        Text_URL = result['source']
        Text_content = requests.get(Text_URL).text
        source_language      = result['source_language']
        destination_language = result['destination_language']
        translation_service  = result['translation_service']
        
        if destination_language:
            if destination_language == 'en':
                return getpollyaudio(Text_content,'long')
            else:
                if translation_service:
                    try:
                        if translation_service == 'google':
                            translator = Translator()
                            translation = translator.translate(Text_content,src=source_language,dest=destination_language)
                            Text_content = translation.text
                            return getpollyaudio(Text_content,'long')
                        else: 
                            pass
                    except Exception as e:
                        return getpollyaudio(Text_content,'long')
                else:
                    return getpollyaudio(Text_content,'long')
        else:
            return getpollyaudio(Text_content,'long')

def getpollyaudio(text,type):
    now = datetime.datetime.now()
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
        
    split_string = lambda x, n: [x[i:i+n] for i in range(0, len(x), n)]
    sounds       = []
    mp3_content=[]
    
    if type == 'long':
        splitted_text= split_string(str(text),1500)
        length = len(splitted_text)
        filename   = 'polly_longfile'+str(date_time)+'.mp3'
    else:    
        splitted_text= split_string(str(text),1000)
        length = 1
        filename   = 'polly_shortfile'+str(date_time)+'.mp3'
        
    
    for l in range(0,length):
        response = polly.synthesize_speech(Text=str(splitted_text[l]), OutputFormat="mp3", VoiceId="Joey") 
        with closing(response["AudioStream"]) as stream:
            f= open(filename, "a+b")
            f.write(stream.read())
            
    bucket_name = 'amazon-polly'
    s3.upload_file(filename, bucket_name, filename,
        ExtraArgs={'ACL': 'public-read'}
    )
    s3_url = 'https://s3-us-west-2.amazonaws.com/%s/%s' % (bucket_name, filename)            
    
    return str(s3_url) 
    
#END    
    
@app.route('/get_text',methods=['GET','POST'])
def get_text(option=''):
    result = requests.get('https://lighthouse247.com//shared_services/babel/babel_test.php?case=1').json()
    if 'source' in result:
        Text_URL = result['source']
        Text_content = requests.get(Text_URL).text
        source_language      = result['source_language']
        destination_language = result['destination_language']
        translation_service  = result['translation_service']
        try:                             
            if 'option' in request.args: 
                option = request.args.get('option')
        except Exception as e:
            option = ''
            
        if destination_language:
            if destination_language == 'en':
                return Text_content
            else:
                if translation_service and (option==('6' or 6) or option==('7' or 7)):
                    try:
                        if translation_service == 'google':
                            translator = Translator()
                            translation = translator.translate(Text_content,src=source_language,dest=destination_language)
                            Text_content = translation.text
                            return Text_content
                        else: 
                            ##amazon translator
                            pass
                    except Exception as e:
                        return Text_content
                else:
                    return Text_content
        else:
            return Text_content
            
@app.route('/get_shortaudio',methods=['GET','POST'])
def get_shortaudio(combined_url='',option='',limit='1'):
    now = datetime.datetime.now()
    
    try:
        if 'option' in request.args:
            option = request.args.get('option')
    except Exception as e:
        option=''
        
    split_string = lambda x, n: [x[i:i+n] for i in range(0, len(x), n)]
    sounds       = []
    
    if limit=='1':
        length=1
        splitted_text= split_string(str(get_text(option)),1000)
    else:
        splitted_text= split_string(str(get_text(option)),500)
        length=len(splitted_text)   
    # l=0
    # response = polly.synthesize_speech(Text=str(splitted_text[l]), OutputFormat="mp3", VoiceId="Joey")
        
    # if "AudioStream" in response:
        # # Note: Closing the stream is important as the service throttles on the
        # # number of parallel connections. Here we are using contextlib.closing to
        # # ensure the close method of the stream object will be called automatically
        # # at the end of the with statement's scope.
        # with closing(response["AudioStream"]) as stream:
            # output = "speech"+str(l)+"_"+str(date_time)+".mp3"

            # try:
                # # Open a file for writing the output as a binary stream
                # with open(output, "wb") as file:
                    # file.write(stream.read())
                # bucket_name = 'amazon-polly'
                # filename    = output
                # s3.upload_file(filename, bucket_name, filename,
                    # ExtraArgs={'ACL': 'public-read'}
                # )
                # s3_url = 'https://s3-us-west-2.amazonaws.com/%s/%s' % (bucket_name, filename)
                # sounds.append(s3_url)
            # except IOError as error:
                # # Could not write to file, exit gracefully
                # print(error)
                # #sys.exit(-1)                       
    # else:
        # # The response didn't contain audio data, exit gracefully
        # print("Could not stream audio")
        # #sys.exit(-1)
        
    for l in range(0,length):
        date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
        output = "speech"+str(l)+"_"+str(date_time)+".mp3"
        sounds.append(output)
        Thread(target = make_URLs_ready(length,sounds,splitted_text,l)).start()   

    short_s3urls=[]
    for url in sounds:
        short_s3urls.append(str("https://s3-us-west-2.amazonaws.com/amazon-polly/"+str(url)))
            
    if limit=='full':            
        #r = requests.post('https://amazon-polly-mergemp3.herokuapp.com/', json = {'Files_To_Merge':sounds,"combined_url":combined_url},headers={'Content-type': 'application/json'}) 
        
        # scheduler = BackgroundScheduler()
        # scheduler.start()    
        # scheduler.add_job(
            # func=lambda: make_URLs_ready(length,Short_ulrs,splitted_text),
            # id='longaudio',
            # name="contains splitted mp3's",
            # replace_existing=True)
        # atexit.register(lambda: scheduler.shutdown())
        #time.sleep(5)
        
        
        r = requests.post('https://amazon-polly-mergemp3.herokuapp.com/', json = {'Files_To_Merge':short_s3urls,"combined_url":combined_url},headers={'Content-type': 'application/json'})
        return str("https://s3-us-west-2.amazonaws.com/amazon-polly/"+str(combined_url))
    else:  
        return json.dumps(short_s3urls)
        #return json.dumps(sounds)   
        #return json.dumps(["https://s3-us-west-2.amazonaws.com/amazon-polly/speech0_2018-02-01_14-37-17.mp3", "https://s3-us-west-2.amazonaws.com/amazon-polly/speech1_2018-02-01_14-37-17.mp3", "https://s3-us-west-2.amazonaws.com/amazon-polly/speech2_2018-02-01_14-37-17.mp3"])    

    
def make_URLs_ready(length,urls,splitted_text,l):
    #for l in range(1,length):
    # Request speech synthesis
    response = polly.synthesize_speech(Text=str(splitted_text[l]), OutputFormat="mp3", VoiceId="Joey")
    if "AudioStream" in response:
        # Note: Closing the stream is important as the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
        with closing(response["AudioStream"]) as stream:
            #output = "speech"+str(l)+"_"+str(date_time)+".mp3"
            output = urls[l]

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
                #sounds.append(s3_url)
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                #sys.exit(-1)                       
    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        #sys.exit(-1)
    return ''            
        
@app.route('/get_longaudio',methods=['GET','POST'])
def get_longaudio(option=''):
    now = datetime.datetime.now()
    date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
    combined_url = "combined_"+str(now.strftime("%Y-%m-%d-%H-%M-%S"))+str(".mp3")
    if 'option' in request.args:
        option = request.args.get('option')

    scheduler = BackgroundScheduler()
    scheduler.start()    
    scheduler.add_job(
        func=lambda: get_shortaudio(combined_url,option,'full'),
        id='longsudio',
        name='merging mp3 files',
        replace_existing=True)
    atexit.register(lambda: scheduler.shutdown())
    
    #urls = get_shortaudio(combined_url,option,'full')
    #url = json.loads(get_shortaudio(combined_url,option,1))
    
    #short_audio_urls = get_shortaudio(option,'full')
    #r = requests.post('http://localhost/AmazonPolly_mp3merge_api/index.php', json = {'Files_To_Merge':json.loads(short_audio_urls),"combined_url":combined_url},headers={'Content-type': 'application/json'})
    
    #return str(r.json()['combined_mp3'])
    return str("https://s3-us-west-2.amazonaws.com/amazon-polly/"+str(combined_url))
    #return json.dumps(urls)

      


if __name__ == '__main__':
    #app.run(debug = True)
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
