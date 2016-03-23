# coding:utf-8
import sys
import config
import urllib
from tornado import gen
from util.json_util import JsonUtil
from jenkins import Jenkins
from dbopt.jsonobjs import build, build_detail, createrespo, delbuild, delrespo, getbuilds, postimagesync, postbuild, \
    callback, jobinfo, hook, image, postimage
from tornado import gen
from requests.exceptions import RequestException, HTTPError
from datetime import datetime
import jsonpickle
from . import utils
import xmltodict

reload(sys)
sys.setdefaultencoding('utf-8')


class jenkinscls(object):
    def __init__(self):
        self.url = config.JENKINS_URL
        self.username = config.JENKINS_NAME
        self.token = config.JENKINS_TOKEN
        self.j = Jenkins(config.JENKINS_URL, username=config.JENKINS_NAME, password=config.JENKINS_TOKEN)

    def getjobnames(self, strval=''):
        rs = {r'...': r'/'}
        s = utils.multiple_replace(str(strval), rs).split('/')
        return s[0], "/".join(s[1:])

    def getlenstr(self, strval, n):
        return str(strval)[0:n]

    def getstatus(self, strval):
        if str(strval) == 'FAILURE':
            return 'error'
        elif str(strval) == 'ABORTED':
            return 'aborted'
        elif str(strval) == 'SUCCESS':
            return 'success'
        else:
            return 'started'

    def edit_userjob_config(self, jn, obj):
        n, r = self.getjobnames(jn)
        try:
            desobj = callback()
            desobj.des = obj['description']
            desobj.callback_url = ""
            desobj.build_id = ''
            desobj.duration = ''
            desobj.namespace = n
            desobj.image_name=obj['image_name']
            desobj.repo_name = r
            desobj.status = ''
            desobj.tag = obj['build_config']['tag_configs']['docker_repo_tag']
            desobj.time = ''

            ss = xmltodict.parse(self.getbasejob_config())
            jsonpickle.set_preferred_backend('json')
            ss['project']['description'] = jsonpickle.encode(desobj)
            ss['project']['properties']['com.tikal.hudson.plugins.notification.HudsonNotificationProperty']['endpoints'] \
                ['com.tikal.hudson.plugins.notification.Endpoint']['url'] = config.JOBHOOKURL

            ss['project']['scm']['userRemoteConfigs']['hudson.plugins.git.UserRemoteConfig'] \
                ['url'] = obj['build_config']['code_repo_clone_url']
            ss['project']['scm']['branches']['hudson.plugins.git.BranchSpec'] \
                ['name'] = '*/' + obj['build_config']['tag_configs']['code_repo_type_value']
            ss['project']['builders']['hudson.tasks.Shell']['command'] = config.JOBCOMMON1
            ss['project']['builders']['com.cloudbees.dockerpublish.DockerBuilder']['registry'] \
                ['url'] = config.REGISTRYURL
            b = str(obj['build_config']['tag_configs']['build_cache_enabled'])
            ss['project']['builders']['com.cloudbees.dockerpublish.DockerBuilder']['noCache'] \
                = ('true' if b == 'false' else 'false')
            ss['project']['builders']['com.cloudbees.dockerpublish.DockerBuilder']['dockerfilePath'] \
                = obj['build_config']['tag_configs']['dockerfile_location']
            ss['project']['builders']['com.cloudbees.dockerpublish.DockerBuilder']['repoTag'] \
                = obj['build_config']['tag_configs']['docker_repo_tag']
            ss['project']['builders']['com.cloudbees.dockerpublish.DockerBuilder']['repoName'] \
                = obj['image_name']

            return xmltodict.unparse(ss)
        except Exception as e:
            print e.message

    def edit_docker_load_job_config(self, obj):

        try:
            # {docker_login} && docker import {httpfilename} {imagename} && docker push {imagename}
            ss = xmltodict.parse(self.getdocker_load_config())
            desobj = callback()
            desobj.des = obj['export_file_url']
            desobj.callback_url = obj['post_callback_url']
            desobj.build_id =  obj['build_id']
            desobj.duration = ''
            desobj.namespace = ""
            desobj.repo_name = ""
            desobj.image_name= obj['image_name']
            desobj.status = ''
            desobj.tag = obj['tag']
            desobj.time = ''
            jsonpickle.set_preferred_backend('json')
            ss['project']['description'] = jsonpickle.encode(desobj)
            ss['project']['properties']['com.tikal.hudson.plugins.notification.HudsonNotificationProperty']['endpoints'] \
                ['com.tikal.hudson.plugins.notification.Endpoint']['url'] = config.JOBHOOKURL
            tempstr = str(ss['project']['builders']['hudson.tasks.Shell']['command'])
            s = {r'{docker_login}': config.JOBCOMMON1, r'{httpfilename}': obj['export_file_url'],
                 r'{imagename}': config.REGISTRYNAME + '/' + obj['image_name'] + ':' + obj['tag']}
            ss['project']['builders']['hudson.tasks.Shell']['command'] = utils.multiple_replace(tempstr, s)

            return xmltodict.unparse(ss)
        except Exception as e:
            print e.message


    def edit_docker_sync_job_config(self, obj):

        try:
            # {docker_login} && docker pull {oldimage} && docker tag {oldimage} {newimage} && docker push {newimage}
            ss = xmltodict.parse(self.getdocker_sync_config())
            jsonUtil = JsonUtil()
            c = jsonUtil.parseJsonString(config.CLOUD_CONFIG)
            cid = obj['sync_cloud_id']
            desobj = callback()
            desobj.des = ""
            desobj.callback_url = obj['post_callback_url']
            desobj.build_id = ''
            desobj.duration = ''
            desobj.namespace = ""
            desobj.repo_name = obj['sync_cloud_id'] # 把cloudid 临时存在 这
            desobj.image_name= obj['image_name']
            desobj.status = ''
            desobj.tag = obj['tag']
            desobj.time = ''
            jsonpickle.set_preferred_backend('json')
            ss['project']['description'] = jsonpickle.encode(desobj)
            ss['project']['properties']['com.tikal.hudson.plugins.notification.HudsonNotificationProperty']['endpoints'] \
                ['com.tikal.hudson.plugins.notification.Endpoint']['url'] = config.JOBHOOKURL+'?cloudid='+obj['sync_cloud_id']
            tempstr = str(ss['project']['builders']['hudson.tasks.Shell']['command'])
            s = {r'{docker_login}': c[cid]['login_common'],
                 r'{oldimage}': config.REGISTRYNAME + '/' + obj['image_name'] + ':' + obj['tag'],
                 r'{newimage}': c[cid]['registry_name'] + '/' + obj['image_name'] + ':' + obj['tag']}
            ss['project']['builders']['hudson.tasks.Shell']['command'] = utils.multiple_replace(tempstr, s)

            return xmltodict.unparse(ss)
        except Exception as e:
            print e.message

    def updateconfig_buildid(self, jn, imagename,build_id, callback_url):
        try:
            ss = xmltodict.parse(self.j.get_job_config(jn))
            jsonpickle.set_preferred_backend('json')
            desobj = jsonpickle.decode(ss['project']['description'])
            if str(desobj.build_id) == str(build_id):
                return True
            desobj.build_id = build_id
            desobj.callback_url = callback_url
            desobj.image_name=imagename
            ss['project']['description'] = jsonpickle.encode(desobj)

            self.j.reconfig_job(jn, xmltodict.unparse(ss))

            return True
        except Exception as e:
            print e.message
            return False

    @gen.coroutine
    def posthook(self, obj):
        # s = {r'/': r'...'}
        jn = obj['name']
        bid = str(obj['build']['number'])
        # n, r = self.getjobnames(jn)
        re = hook()
        try:
            info = self.j.get_build_info(jn, int(bid))
            if self.j.job_exists(jn):
                ss = xmltodict.parse(self.j.get_job_config(jn))
                jsonpickle.set_preferred_backend('json')

                if isinstance(jsonpickle.decode(ss['project']['description']), callback):
                    desobj = jsonpickle.decode(ss['project']['description'])
                    re.namespace = desobj.namespace
                    re.repo_name = desobj.repo_name
                    re.build_id = str(obj['build']['number'])
                    re.status = self.getstatus(obj['build']['status'])
                    re.duration = info['duration']
                    re.tag = desobj.tag
                    re.time = datetime.now()
                    re.callurl = desobj.callback_url
        except Exception as e:
            print e.message
            re = None
        raise gen.Return(re)
    @gen.coroutine
    def post_docker_load_hook(self, obj):

        jn = obj['name']
        bid = str(obj['build']['number'])

        re = postimage()
        try:
            # info = self.j.get_build_info(jn, int(bid))
            if self.j.job_exists(jn):
                ss = xmltodict.parse(self.j.get_job_config(jn))
                jsonpickle.set_preferred_backend('json')

                if isinstance(jsonpickle.decode(ss['project']['description']), callback):
                    desobj = jsonpickle.decode(ss['project']['description'])
                    re.image_name=desobj.image_name
                    re.status = self.getstatus(obj['build']['status'])
                    re.tag = desobj.tag
                    re.export_file_url=desobj.des
                    re.time = datetime.now()
                    re.build_id=desobj.build_id
                    re.post_callback_url = desobj.callback_url
                    if re.status!='error' and config.JENKINS_IMAGEOPTJOB_DELETE=='true':
                        self.j.delete_job(jn)


        except Exception as e:
            print e.message
            re = None
        raise gen.Return(re)
    @gen.coroutine
    def post_docker_sync_hook(self, obj,cloudid):
        jn = obj['name']
        # bid = str(obj['build']['number'])
        jsonUtil = JsonUtil()
        c = jsonUtil.parseJsonString(config.CLOUD_CONFIG)
        j = Jenkins(c[cloudid]['jenkins_url'], username=c[cloudid]['jenkins_name'], password=c[cloudid]['jenkins_token'])

        re = postimagesync()
        try:

            if j.job_exists(jn):
                ss = xmltodict.parse(j.get_job_config(jn))
                jsonpickle.set_preferred_backend('json')

                if isinstance(jsonpickle.decode(ss['project']['description']), callback):
                    desobj = jsonpickle.decode(ss['project']['description'])
                    re.image_name=desobj.image_name
                    re.status = self.getstatus(obj['build']['status'])
                    re.sync_cloud_id=desobj.repo_name
                    re.tag = desobj.tag
                    re.time = datetime.now()
                    re.post_callback_url = desobj.callback_url
                    if re.status!='error' and config.JENKINS_IMAGEOPTJOB_DELETE=='true':
                        j.delete_job(jn)


        except Exception as e:
            print e.message
            re = None
        raise gen.Return(re)
    @gen.coroutine
    def createjob(self, jobname, obj):
        s = {r'/': r'...'}
        jn = utils.multiple_replace(jobname, s)
        n, r = self.getjobnames(jn)
        try:
            if self.j.job_exists(jn):
                re = createrespo(n, r, '工程已存在', 'error', datetime.now())
            self.j.create_job(jn, self.edit_userjob_config(jn, obj))
            re = createrespo(n, r, '', 'success', datetime.now())
        except Exception as e:
            print e.message
            re = createrespo(n, r, '', 'error', datetime.now())
        raise gen.Return(re)

    @gen.coroutine
    def create_docker_load_job(self, obj):
        # s = {r'/': r'...'}
        # jn = utils.multiple_replace(jobname, s)
        s = utils.randomstr(8)
        jn = '__docker_load_job_' + s
        re = postimage()
        re.created_at = datetime.now()
        re.image_name = obj['image_name']
        re.build_id=str(obj['build_id'])
        re.post_callback_url = obj['post_callback_url']
        re.tag = obj['tag']
        re.status = 'started'
        try:
            if self.j.job_exists(jn):
                jn = jn + utils.randomstr(4)
                x=self.edit_docker_load_job_config(obj)
                self.j.create_job(jn, x)
                yield gen.sleep(0.5)
                self.j.build_job(jn)
            x=self.edit_docker_load_job_config( obj)
            self.j.create_job(jn, x)
            yield gen.sleep(0.5)
            self.j.build_job(jn)

        except Exception as e:
            print e.message
            re.status = 'error'
        raise gen.Return(re)

    @gen.coroutine
    def create_docker_sync_job(self, obj):
        # s = {r'/': r'...'}
        # jn = utils.multiple_replace(jobname, s)
        s = utils.randomstr(8)
        jn = '__docker_sync_job_' + s
        cid = obj['sync_cloud_id']
        jsonUtil = JsonUtil()
        c = jsonUtil.parseJsonString(config.CLOUD_CONFIG)
        j = Jenkins(c[cid]['jenkins_url'], username=c[cid]['jenkins_name'], password=c[cid]['jenkins_token'])
        re = postimagesync()
        re.time = datetime.now()
        re.sync_cloud_id = obj['sync_cloud_id']
        re.image_name = obj['image_name']
        re.post_callback_url = obj['post_callback_url']
        re.tag = obj['tag']
        re.status = 'started'
        try:
            if j.job_exists(jn):
                jn = jn + utils.randomstr(4)
                j.create_job(jn, self.edit_docker_sync_job_config(obj))
                yield gen.sleep(0.5)
                j.build_job(jn)
            j.create_job(jn, self.edit_docker_sync_job_config(obj))
            yield gen.sleep(0.5)
            j.build_job(jn)
        except Exception as e:
            print e.message
            re.status = 'error'
        raise gen.Return(re)

    @gen.coroutine
    def editjob(self, jobname, obj):
        s = {r'/': r'...'}
        jn = utils.multiple_replace(jobname, s)
        n, r = self.getjobnames(jn)
        try:
            if self.j.job_exists(jn):
                self.j.reconfig_job(jn, self.edit_userjob_config(jn, obj))
                re = createrespo(n, r, '', 'success', datetime.now())
            else:
                re = createrespo(n, r, 'repo is not find', 'error', datetime.now())
        except Exception as e:
            print e.message
            re = createrespo(n, r, '', 'error', datetime.now())
        raise gen.Return(re)

    @gen.coroutine
    def getjobinfo(self, jobname):
        s = {r'/': r'...'}
        jn = utils.multiple_replace(jobname, s)
        n, r = self.getjobnames(jn)
        re = jobinfo()
        try:
            if self.j.job_exists(jn):
                re.namespace = n
                re.repo_name = r
                re.info = self.j.get_job_info(jn)
        except Exception as e:
            print e.message
            re.namespace = n
            re.repo_name = r
            re.info = ""
        raise gen.Return(re)

    @gen.coroutine
    def deljob(self, jobname):
        s = {r'/': r'...'}
        jn = utils.multiple_replace(jobname, s)
        n, r = self.getjobnames(jn)
        try:
            if self.j.job_exists(jn):
                self.j.delete_job(jn)
            re = delrespo(n, r, 'success')

        except Exception as e:
            print e.message
            re = delrespo(n, r, 'error')
        raise gen.Return(re)

    @gen.coroutine
    def stopbuild(self, jobname, build_id):
        s = {r'/': r'...'}
        jn = utils.multiple_replace(jobname, s)
        n, r = self.getjobnames(jn)
        try:
            if self.j.job_exists(jn) and self.j.get_build_info(jn, int(build_id)):
                self.j.stop_build(jn, int(build_id))
                re = delbuild(n, r, build_id, 'aborted')
            else:
                re = delbuild(n, r, build_id, 'error')

        except Exception as e:
            print e.message
            re = delbuild(n, r, build_id, 'error')
        raise gen.Return(re)

    @gen.coroutine
    def postbuild(self, jobname, imagename, tag, callback_url):
        s = {r'/': r'...'}
        jn = utils.multiple_replace(jobname, s)
        n, r = self.getjobnames(jn)
        try:

            if self.j.job_exists(jn):

                j = self.j.get_job_info(jn)

                build_id = j['nextBuildNumber']

                if self.j.get_queue_info() != []:
                    re = postbuild(n, r, imagename,build_id, tag, datetime.now(), 'queue')
                elif j['queueItem'] != None:
                    re = postbuild(n, r,imagename, build_id, tag, datetime.now(), 'queue')
                else:
                    self.updateconfig_buildid(jn, imagename,build_id, callback_url)
                    self.j.build_job(jn)
                    re = postbuild(n, r,imagename, build_id, tag, datetime.now(), 'started')
            else:
                re = postbuild(n, r, '', '', datetime.now(), 'error')

        except Exception as e:
            print e.message
            re = postbuild(n, r, '', tag, datetime.now(), 'error')
        raise gen.Return(re)

    @gen.coroutine
    def getbuild(self, jobname, build_id):
        s = {r'/': r'...'}
        jn = utils.multiple_replace(jobname, s)
        n, r = self.getjobnames(jn)
        try:
            b = self.j.get_build_info(jn, int(build_id))
            building = b['building']
            duration = b['duration']
            dt = self.getlenstr(b['timestamp'], 10)
            started_at = utils.timestamp_datetime(int(dt))
            status = self.getstatus(b['result'])
            stdout = self.j.get_build_console_output(jn, int(build_id))
            bd = build_detail(n, r, build_id, building, started_at, duration, status, stdout)
        except Exception as e:
            print e.message
            bd = build_detail(n, r, build_id, '', '', '', 'error', '')
        raise gen.Return(bd)

    def getdocker_sync_config(self):
        s = '''<?xml version='1.0' encoding='UTF-8'?>
<project>
  <actions/>
  <description></description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <com.tikal.hudson.plugins.notification.HudsonNotificationProperty plugin="notification@1.10">
      <endpoints>
        <com.tikal.hudson.plugins.notification.Endpoint>
          <protocol>HTTP</protocol>
          <format>JSON</format>
          <url>http://10.1.39.60:8080/v1/hook</url>
          <event>completed</event>
          <timeout>30000</timeout>
          <loglines>0</loglines>
        </com.tikal.hudson.plugins.notification.Endpoint>
      </endpoints>
    </com.tikal.hudson.plugins.notification.HudsonNotificationProperty>
    <com.synopsys.arc.jenkins.plugins.ownership.jobs.JobOwnerJobProperty plugin="ownership@0.8"/>
    <hudson.plugins.heavy__job.HeavyJobProperty plugin="heavy-job@1.1">
      <weight>1</weight>
    </hudson.plugins.heavy__job.HeavyJobProperty>
    <jenkins.model.BuildDiscarderProperty>
      <strategy class="hudson.tasks.LogRotator">
        <daysToKeep>30</daysToKeep>
        <numToKeep>50</numToKeep>
        <artifactDaysToKeep>-1</artifactDaysToKeep>
        <artifactNumToKeep>-1</artifactNumToKeep>
      </strategy>
    </jenkins.model.BuildDiscarderProperty>
    <job-metadata plugin="metadata@1.1.0b">
      <values class="linked-list">
        <metadata-tree>
          <name>job-info</name>
          <parent class="job-metadata" reference="../../.."/>
          <generated>true</generated>
          <exposedToEnvironment>false</exposedToEnvironment>
          <children class="linked-list">
            <metadata-tree>
              <name>last-saved</name>
              <description></description>
              <parent class="metadata-tree" reference="../../.."/>
              <generated>true</generated>
              <exposedToEnvironment>false</exposedToEnvironment>
              <children class="linked-list">
                <metadata-date>
                  <name>time</name>
                  <description></description>
                  <parent class="metadata-tree" reference="../../.."/>
                  <generated>true</generated>
                  <exposedToEnvironment>false</exposedToEnvironment>
                  <value>
                    <time>1458098001639</time>
                    <timezone>Asia/Shanghai</timezone>
                  </value>
                  <checked>false</checked>
                </metadata-date>
                <metadata-tree>
                  <name>user</name>
                  <parent class="metadata-tree" reference="../../.."/>
                  <generated>true</generated>
                  <exposedToEnvironment>false</exposedToEnvironment>
                  <children class="linked-list">
                    <metadata-string>
                      <name>display-name</name>
                      <description></description>
                      <parent class="metadata-tree" reference="../../.."/>
                      <generated>true</generated>
                      <exposedToEnvironment>false</exposedToEnvironment>
                      <value>admin</value>
                    </metadata-string>
                    <metadata-string>
                      <name>full-name</name>
                      <description></description>
                      <parent class="metadata-tree" reference="../../.."/>
                      <generated>true</generated>
                      <exposedToEnvironment>false</exposedToEnvironment>
                      <value>admin</value>
                    </metadata-string>
                  </children>
                </metadata-tree>
              </children>
            </metadata-tree>
          </children>
        </metadata-tree>
      </values>
    </job-metadata>
  </properties>
  <scm class="hudson.scm.NullSCM"/>
  <scmCheckoutRetryCount>3</scmCheckoutRetryCount>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.Shell>
      <command>{docker_login} &amp;&amp; docker pull {oldimage} &amp;&amp; docker tag --force=true {oldimage} {newimage} &amp;&amp; docker push {newimage}
</command>
    </hudson.tasks.Shell>
  </builders>
  <publishers/>
  <buildWrappers>
    <hudson.plugins.ansicolor.AnsiColorBuildWrapper plugin="ansicolor@0.4.2">
      <colorMapName>xterm</colorMapName>
    </hudson.plugins.ansicolor.AnsiColorBuildWrapper>
  </buildWrappers>
</project>'''
        return s

    def getdocker_load_config(self):
        s = '''<?xml version='1.0' encoding='UTF-8'?>
<project>
  <actions/>
  <description></description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <com.tikal.hudson.plugins.notification.HudsonNotificationProperty plugin="notification@1.10">
      <endpoints>
        <com.tikal.hudson.plugins.notification.Endpoint>
          <protocol>HTTP</protocol>
          <format>JSON</format>
          <url>http://10.1.39.60:8080/v1/hook</url>
          <event>completed</event>
          <timeout>30000</timeout>
          <loglines>0</loglines>
        </com.tikal.hudson.plugins.notification.Endpoint>
      </endpoints>
    </com.tikal.hudson.plugins.notification.HudsonNotificationProperty>
    <com.synopsys.arc.jenkins.plugins.ownership.jobs.JobOwnerJobProperty plugin="ownership@0.8"/>
    <hudson.plugins.heavy__job.HeavyJobProperty plugin="heavy-job@1.1">
      <weight>1</weight>
    </hudson.plugins.heavy__job.HeavyJobProperty>
    <jenkins.model.BuildDiscarderProperty>
      <strategy class="hudson.tasks.LogRotator">
        <daysToKeep>30</daysToKeep>
        <numToKeep>50</numToKeep>
        <artifactDaysToKeep>-1</artifactDaysToKeep>
        <artifactNumToKeep>-1</artifactNumToKeep>
      </strategy>
    </jenkins.model.BuildDiscarderProperty>
    <job-metadata plugin="metadata@1.1.0b">
      <values class="linked-list">
        <metadata-tree>
          <name>job-info</name>
          <parent class="job-metadata" reference="../../.."/>
          <generated>true</generated>
          <exposedToEnvironment>false</exposedToEnvironment>
          <children class="linked-list">
            <metadata-tree>
              <name>last-saved</name>
              <description></description>
              <parent class="metadata-tree" reference="../../.."/>
              <generated>true</generated>
              <exposedToEnvironment>false</exposedToEnvironment>
              <children class="linked-list">
                <metadata-date>
                  <name>time</name>
                  <description></description>
                  <parent class="metadata-tree" reference="../../.."/>
                  <generated>true</generated>
                  <exposedToEnvironment>false</exposedToEnvironment>
                  <value>
                    <time>1458097635464</time>
                    <timezone>Asia/Shanghai</timezone>
                  </value>
                  <checked>false</checked>
                </metadata-date>
                <metadata-tree>
                  <name>user</name>
                  <parent class="metadata-tree" reference="../../.."/>
                  <generated>true</generated>
                  <exposedToEnvironment>false</exposedToEnvironment>
                  <children class="linked-list">
                    <metadata-string>
                      <name>display-name</name>
                      <description></description>
                      <parent class="metadata-tree" reference="../../.."/>
                      <generated>true</generated>
                      <exposedToEnvironment>false</exposedToEnvironment>
                      <value>admin</value>
                    </metadata-string>
                    <metadata-string>
                      <name>full-name</name>
                      <description></description>
                      <parent class="metadata-tree" reference="../../.."/>
                      <generated>true</generated>
                      <exposedToEnvironment>false</exposedToEnvironment>
                      <value>admin</value>
                    </metadata-string>
                  </children>
                </metadata-tree>
              </children>
            </metadata-tree>
          </children>
        </metadata-tree>
      </values>
    </job-metadata>
  </properties>
  <scm class="hudson.scm.NullSCM"/>
  <scmCheckoutRetryCount>3</scmCheckoutRetryCount>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.Shell>
      <command>{docker_login} &amp;&amp; docker import {httpfilename} {imagename} &amp;&amp; docker push {imagename}
</command>
    </hudson.tasks.Shell>
  </builders>
  <publishers/>
  <buildWrappers>
    <hudson.plugins.ansicolor.AnsiColorBuildWrapper plugin="ansicolor@0.4.2">
      <colorMapName>xterm</colorMapName>
    </hudson.plugins.ansicolor.AnsiColorBuildWrapper>
  </buildWrappers>
</project>'''
        return s

    def getbasejob_config(self):
        s = '''<?xml version='1.0' encoding='UTF-8'?>
<project>
  <actions/>
  <description></description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <com.tikal.hudson.plugins.notification.HudsonNotificationProperty plugin="notification@1.10">
      <endpoints>
        <com.tikal.hudson.plugins.notification.Endpoint>
          <protocol>HTTP</protocol>
          <format>JSON</format>
          <url>http://10.1.39.60:8080/v1/hook</url>
          <event>completed</event>
          <timeout>30000</timeout>
          <loglines>0</loglines>
        </com.tikal.hudson.plugins.notification.Endpoint>
      </endpoints>
    </com.tikal.hudson.plugins.notification.HudsonNotificationProperty>
    <com.synopsys.arc.jenkins.plugins.ownership.jobs.JobOwnerJobProperty plugin="ownership@0.8"/>
    <hudson.plugins.heavy__job.HeavyJobProperty plugin="heavy-job@1.1">
      <weight>1</weight>
    </hudson.plugins.heavy__job.HeavyJobProperty>
    <jenkins.model.BuildDiscarderProperty>
      <strategy class="hudson.tasks.LogRotator">
        <daysToKeep>30</daysToKeep>
        <numToKeep>50</numToKeep>
        <artifactDaysToKeep>-1</artifactDaysToKeep>
        <artifactNumToKeep>-1</artifactNumToKeep>
      </strategy>
    </jenkins.model.BuildDiscarderProperty>
    <job-metadata plugin="metadata@1.1.0b">
      <values class="linked-list">
        <metadata-tree>
          <name>job-info</name>
          <parent class="job-metadata" reference="../../.."/>
          <generated>true</generated>
          <exposedToEnvironment>false</exposedToEnvironment>
          <children class="linked-list">
            <metadata-tree>
              <name>last-saved</name>
              <description></description>
              <parent class="metadata-tree" reference="../../.."/>
              <generated>true</generated>
              <exposedToEnvironment>false</exposedToEnvironment>
              <children class="linked-list">
                <metadata-date>
                  <name>time</name>
                  <description></description>
                  <parent class="metadata-tree" reference="../../.."/>
                  <generated>true</generated>
                  <exposedToEnvironment>false</exposedToEnvironment>
                  <value>
                    <time>1457958794480</time>
                    <timezone>Asia/Shanghai</timezone>
                  </value>
                  <checked>false</checked>
                </metadata-date>
                <metadata-tree>
                  <name>user</name>
                  <parent class="metadata-tree" reference="../../.."/>
                  <generated>true</generated>
                  <exposedToEnvironment>false</exposedToEnvironment>
                  <children class="linked-list">
                    <metadata-string>
                      <name>display-name</name>
                      <description></description>
                      <parent class="metadata-tree" reference="../../.."/>
                      <generated>true</generated>
                      <exposedToEnvironment>false</exposedToEnvironment>
                      <value>admin</value>
                    </metadata-string>
                    <metadata-string>
                      <name>full-name</name>
                      <description></description>
                      <parent class="metadata-tree" reference="../../.."/>
                      <generated>true</generated>
                      <exposedToEnvironment>false</exposedToEnvironment>
                      <value>admin</value>
                    </metadata-string>
                  </children>
                </metadata-tree>
              </children>
            </metadata-tree>
          </children>
        </metadata-tree>
      </values>
    </job-metadata>
  </properties>
  <scm class="hudson.plugins.git.GitSCM" plugin="git@2.4.2">
    <configVersion>2</configVersion>
    <userRemoteConfigs>
      <hudson.plugins.git.UserRemoteConfig>
        <url>https://github.com/zhwenh/dockerfile-jdk-tomcat.git</url>
      </hudson.plugins.git.UserRemoteConfig>
    </userRemoteConfigs>
    <branches>
      <hudson.plugins.git.BranchSpec>
        <name>*/master</name>
      </hudson.plugins.git.BranchSpec>
    </branches>
    <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
    <browser class="hudson.plugins.git.browser.GitLab">
      <url></url>
      <version>7.11</version>
    </browser>
    <submoduleCfg class="list"/>
    <extensions/>
  </scm>
  <scmCheckoutRetryCount>3</scmCheckoutRetryCount>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.Shell>
      <command>docker login -u admin -p admin123 -e registry@asiainfo.com registry.test.com</command>
    </hudson.tasks.Shell>
    <com.cloudbees.dockerpublish.DockerBuilder plugin="docker-build-publish@1.2">
      <server plugin="docker-commons@1.3.1">
        <uri>unix:///var/run/docker.sock</uri>
      </server>
      <registry plugin="docker-commons@1.3.1">
        <url>http://registry.test.com/v2</url>
      </registry>
      <repoName>zhwenh/tomcat</repoName>
      <noCache>false</noCache>
      <forcePull>true</forcePull>
      <dockerfilePath>./Dockerfile</dockerfilePath>
      <skipBuild>false</skipBuild>
      <skipDecorate>false</skipDecorate>
      <repoTag>2.3.1</repoTag>
      <skipPush>false</skipPush>
      <createFingerprint>true</createFingerprint>
      <skipTagLatest>false</skipTagLatest>
      <buildAdditionalArgs></buildAdditionalArgs>
      <forceTag>true</forceTag>
    </com.cloudbees.dockerpublish.DockerBuilder>
  </builders>
  <publishers>
    <hudson.plugins.emailext.ExtendedEmailPublisher plugin="email-ext@2.41.3">
      <recipientList>$DEFAULT_RECIPIENTS</recipientList>
      <configuredTriggers>
        <hudson.plugins.emailext.plugins.trigger.FailureTrigger>
          <email>
            <recipientList>$DEFAULT_RECIPIENTS</recipientList>
            <subject>$PROJECT_DEFAULT_SUBJECT</subject>
            <body>$PROJECT_DEFAULT_CONTENT</body>
            <recipientProviders>
              <hudson.plugins.emailext.plugins.recipients.DevelopersRecipientProvider/>
            </recipientProviders>
            <attachmentsPattern></attachmentsPattern>
            <attachBuildLog>false</attachBuildLog>
            <compressBuildLog>false</compressBuildLog>
            <replyTo>$PROJECT_DEFAULT_REPLYTO</replyTo>
            <contentType>project</contentType>
          </email>
        </hudson.plugins.emailext.plugins.trigger.FailureTrigger>
        <hudson.plugins.emailext.plugins.trigger.SuccessTrigger>
          <email>
            <recipientList>$DEFAULT_RECIPIENTS</recipientList>
            <subject>$PROJECT_DEFAULT_SUBJECT</subject>
            <body>$PROJECT_DEFAULT_CONTENT</body>
            <recipientProviders>
              <hudson.plugins.emailext.plugins.recipients.DevelopersRecipientProvider/>
            </recipientProviders>
            <attachmentsPattern></attachmentsPattern>
            <attachBuildLog>false</attachBuildLog>
            <compressBuildLog>false</compressBuildLog>
            <replyTo>$PROJECT_DEFAULT_REPLYTO</replyTo>
            <contentType>project</contentType>
          </email>
        </hudson.plugins.emailext.plugins.trigger.SuccessTrigger>
      </configuredTriggers>
      <contentType>default</contentType>
      <defaultSubject>$DEFAULT_SUBJECT</defaultSubject>
      <defaultContent>$DEFAULT_CONTENT</defaultContent>
      <attachmentsPattern></attachmentsPattern>
      <presendScript>$DEFAULT_PRESEND_SCRIPT</presendScript>
      <attachBuildLog>false</attachBuildLog>
      <compressBuildLog>false</compressBuildLog>
      <replyTo></replyTo>
      <saveOutput>false</saveOutput>
      <disabled>false</disabled>
    </hudson.plugins.emailext.ExtendedEmailPublisher>
  </publishers>
  <buildWrappers>
    <hudson.plugins.ansicolor.AnsiColorBuildWrapper plugin="ansicolor@0.4.2">
      <colorMapName>xterm</colorMapName>
    </hudson.plugins.ansicolor.AnsiColorBuildWrapper>
  </buildWrappers>
</project>'''

        return s

    @gen.coroutine
    def createbasejob(self):

        s = self.getbasejob_config()

        try:
            self.j.create_job(config.JENKINS_BASEJOB, s)
        except Exception as e:
            print e.message
            raise gen.Return(False)
        raise gen.Return(True)


