DOMAIN = 'http://0.0.0.0'
PORT = '8088'
DB_HOST = '10.1.245.138'
DB_PORT = 27017
DB_NAME = 'test'
DB_USER = 'root'
DB_PWD = 'your password'

REDIS_HOST = '10.1.245.138'
REDIS_PORT =''

JOBHOOKURL = 'http://10.1.39.60:8088/v1/hook'

JOBCOMMON1 ='docker login -u admin -p admin123 -e registry@asiainfo.com registry.test.com'

JENKINS_URL = 'http://10.1.245.138:8080/'
JENKINS_NAME = 'admin'
JENKINS_TOKEN = '1470de62b4d2e1e40acb37057fd91545'
JENKINS_BASEJOB = 'basejob'
JENKINS_IMAGEOPTJOB_DELETE = 'true'

REGISTRYURL = 'http://registry.test.com/v2'
REGISTRYNAME = 'registry.test.com'


AES_KEY = 'your aes key'
TOKEN_TIMEOUT = 60 * 60 * 24 * 30

QINIU_AK = ''
QINIU_SK = ''
QINIU_BUCKET_NAME = ''
QINIU_HOST = ''


CLOUD_CONFIG='{"cloud1":{"jenkins_url":"http://10.1.245.139:8080/","jenkins_name":"admin","jenkins_token":"1470de62b4d2e1e40acb37057fd91545","login_common":"docker login -u admin -p admin123 -e registry@asiainfo.com registry.test.com && docker login -u admin -p admin123 -e registry@asiainfo.com 10.1.245.139","registry_url":"http://10.1.245.139/v2","registry_name":"10.1.245.139"},"cloud2":{"jenkins_url":"http://10.1.245.138:8080/","jenkins_name":"admin","jenkins_token":"1470de62b4d2e1e40acb37057fd91545","login_common":"docker login -u admin -p admin123 -e registry@asiainfo.com registry.test.com","registry_url":"http://registry.test.com/v2","registry_name":"registry.test.com"}}'


