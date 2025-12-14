import urllib.request
import os

os.makedirs('app/static/images', exist_ok=True)
url = 'https://slelguoygbfzlpylpxfs.supabase.co/storage/v1/render/image/public/document-uploads/satly-logo-1765476286568.png'
urllib.request.urlretrieve(url, 'app/static/images/satly-logo.png')
print('Logo downloaded successfully!')
