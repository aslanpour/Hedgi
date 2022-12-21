#put all pics to mybucket

import hashlib
import hmac
import base64


def signi(message, secret):
    message = bytes(message, 'utf-8')
    secret = bytes(secret, 'utf-8')
    #hashlib.sha1
    signature = base64.b64encode(hmac.new(secret, message, digestmod=hashlib.sha256).digest())
    print(signature)
    return signature

def make_digest(message, key):
    
    key = bytes(key, 'UTF-8')
    message = bytes(message, 'UTF-8')
    
    digester = hmac.new(key, message, hashlib.sha1)
    #signature1 = digester.hexdigest()
    signature1 = digester.digest()
    #print(signature1)
    
    #signature2 = base64.urlsafe_b64encode(bytes(signature1, 'UTF-8'))
    signature2 = base64.urlsafe_b64encode(signature1)    
    #print(signature2)
    
    return str(signature2, 'UTF-8')
  # signature=`echo -en ${_signature} | openssl sha1 -hmac ${s3_secret} -binary | base64`
    

from datetime import datetime
date = str(datetime.now())


bucket = 'mybucket130k'
host='10.0.0.91:9000'
s3_key='minioadmin'
s3_secret='minioadmin'

content_type="application/octet-stream"

# _signature="PUT\n\n{0}\n{1}\n{2}".format(content_type, date, resource)

# signature = signi(_signature, s3_secret).decode("utf-8")

header = {}
header['Host'] = host
header['Date'] = date
header['Content-type'] = content_type
# header['Authorization'] = 'AWS {0}:{1}'.format(s3_key, signature)

for i in range(1,83):
    import requests
    file_name='pics-83num-resized-half-6mb-max130kb/pic_{0}.jpg'.format(i)
    with open(file_name, 'rb') as f:
        file_content = f.read()

    resource="/{0}/{1}".format(bucket, file_name.split('/')[-1])
    url = 'http://{0}{1}'.format(host,resource)

    response = requests.put(url=url, headers=header, data=file_content)
    print(response.status_code)
    print(response.headers)

