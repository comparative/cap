# REPLACE ALL xxxx's with your values

TOOL_BASE_URL = 'http://xxxxxxxxxxxxxxxxxx'

CONN_STRING = "host='mypostgres' dbname='cap' user='xxxx'"
SQLALCHEMY_DATABASE_URI = 'postgresql://xxxx@mypostgres/cap'
CELERY_BROKER_URL = 'sqla+postgresql://xxxx@mypostgres/cap'

S3_ACCESS_KEY = 'xxxxxxxxxxxxxxxxxx'
S3_SECRET_KEY = 'xxxxxxxxxxxxxxxxxx'
S3_BUCKET = 'xxxxxxxxxxxxxxxxxx'
S3_URL = 'http://xxxxxxxxxxxxxxxxxx.s3.amazonaws.com/'

# If you run your own export server change the URL below
HIGHCHARTS_EXPORT_URL = 'http://export.highcharts.com'

WTF_CSRF_ENABLED = True
SECRET_KEY = 'random-string-of-your-choosing'
UPLOADS_DEFAULT_DEST = '/var/www/cap/uploads'

SQLALCHEMY_TRACK_MODIFICATIONS = False
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']