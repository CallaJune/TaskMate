# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from webapp2_extras import jinja2

from apiclient.discovery import build
from oauth2client.appengine import OAuth2Decorator

from google.appengine.ext import ndb

import settings, urllib, urllib2, webapp2, logging

YO_URL = "http://api.justyo.co/yo/"

decorator = OAuth2Decorator(client_id=settings.CLIENT_ID,
                            client_secret=settings.CLIENT_SECRET,
                            scope=settings.SCOPE)
service = build('tasks', 'v1')

class Task(ndb.Model):
  yosername = ndb.StringProperty(required=True)
  task_name = ndb.StringProperty(required=True)
  task_id = ndb.StringProperty(required=True)
  task_description = ndb.TextProperty(required=True)
  due_time = ndb.StringProperty(required=True)
  scheduled = ndb.BooleanProperty(required=True)
  
  def destroy(self):
    self.key.delete()
  
  def task_link(self):
    return "/task/{0}".format(self.key.id())

# class YoHandler(webapp2.RequestHandler):
#   def get(self):
#     username = self.request.get('username')
#     url = YO_URL
#     values = {'api_token':settings.YO_API_TOKEN, 'username':username}
#     data = urllib.urlencode(values)
#     req = urllib2.Request(url,data)
#     response = urllib2.urlopen(req)

class MainHandler(webapp2.RequestHandler):
  def render_response(self, template, **context):
    renderer = jinja2.get_jinja2(app=self.app)
    rendered_value = renderer.render_template(template, **context)
    self.response.write(rendered_value)
  @decorator.oauth_aware
  def get(self):
        self.render_response('splash.html')

class HomeHandler(webapp2.RequestHandler):
  def render_response(self, template, **context):
    renderer = jinja2.get_jinja2(app=self.app)
    rendered_value = renderer.render_template(template, **context)
    self.response.write(rendered_value)
  @decorator.oauth_aware
  def get(self):
    if decorator.has_credentials():
      result = service.tasks().list(tasklist='@default').execute(
          http=decorator.http())
      tasks = result.get('items', [])
      for task in tasks:
        task['title_short'] = truncate(task['title'], 20)
      self.render_response('index.html', tasks=tasks)
    else:
      url = decorator.authorize_url()
      self.render_response('index.html', tasks=[], authorize_url=url)

def truncate(s, l):
  return s[:l] + '...' if len(s) > l else s

class TaskHandler(webapp2.RequestHandler):

  def render_response(self, template, **context):
    renderer = jinja2.get_jinja2(app=self.app)
    rendered_value = renderer.render_template(template, **context)
    self.response.write(rendered_value)

  @decorator.oauth_aware
  def get(self, *args, **kwargs):
    task_id = kwargs['task_id']
    task = Task.get_by_id(int(task_id))
    tasks = {
      'title': task.task_name,
      'description': task.task_description,
      'due_time': task.due_time
    }
    if task:
      task.key.delete()

    self.render_response('task.html', task=tasks, authorize_url='none')

class NewHandler(webapp2.RequestHandler):
  @decorator.oauth_aware
  def render_response(self, template, **context):
    renderer = jinja2.get_jinja2(app=self.app)
    rendered_value = renderer.render_template(template, **context)
    self.response.write(rendered_value)

  @decorator.oauth_aware
  def get(self):
    if decorator.has_credentials():
      result = service.tasks().list(tasklist='@default').execute(
          http=decorator.http())
      tasks = result.get('items', [])
      for task in tasks:
        task['title_short'] = truncate(task['title'], 20)
      self.render_response('new.html', tasks=tasks)
    else:
      url = decorator.authorize_url()
      self.render_response('new.html', tasks=[], authorize_url=url)

class ProcessingHandler(webapp2.RequestHandler):
  def get(self):
    #comment process calculation
    query = Task.query()
    query = query.fetch()
    for task in query:
      if task.scheduled == False:
        task.scheduled = True
        task.put()
        username = task.yosername
        link = 'http://task-mate.appspot.com/' + task.task_link()
        url = YO_URL
        values = {'api_token':settings.YO_API_TOKEN, 'username':username, 'link':link}
        data = urllib.urlencode(values)
        req = urllib2.Request(url,data)
        response = urllib2.urlopen(req)

    self.render_response('loader.html', task=[], authorize_url='none')

class CreateHandler(webapp2.RequestHandler):
  def render_response(self, template, **context):
    renderer = jinja2.get_jinja2(app=self.app)
    rendered_value = renderer.render_template(template, **context)
    self.response.write(rendered_value)

  @decorator.oauth_aware
  def get(self):  
        template_values = {}
        taskname = self.request.get('taskname')
        taskdescription = self.request.get('taskdescription')

        #transfer taskdue into 2014-11-03T12:00:00.000Z format
        pretaskdue = self.request.get('taskdue')
        taskdue = pretaskdue[:10] + 'T' + pretaskdue[11:] + ':00.000Z'

        template_values['taskname'] = taskname
        template_values['taskdescription'] = taskdescription
        template_values['taskdue'] = taskdue
        #create a task with all that information and do everything with yo
        tasks = {
          'title': taskname,
          'notes': taskdescription,
          'due': taskdue
          }

        tasks = service.tasks().insert(tasklist='@default', body=tasks).execute(http=decorator.http())
        
        task = Task(yosername = 'CHIVAS604',
        task_name = taskname,
        task_id = tasks['id'],
        task_description = taskdescription,
        due_time = taskdue,
        scheduled = False)
        task.put()

        self.redirect('/home')

routes = [
    webapp2.Route('/', MainHandler, name='splash'),
    webapp2.Route('/home', HomeHandler, name='home'),
    webapp2.Route('/new', NewHandler, name='new'),
    webapp2.Route('/task/<task_id:\d+>', handler=TaskHandler, name='task'),
    webapp2.Route('/processing', ProcessingHandler, name='process'),
    webapp2.Route('/create', CreateHandler, name='create'),
    webapp2.Route(decorator.callback_path, decorator.callback_handler(), name='callback'),
    # webapp2.Route('/yo', YoHandler, name='yo'), 
    # webapp2.Route('/yo/recieve', YoReceiveHandler, name='yoRecieve')
    ]

application = webapp2.WSGIApplication(routes, debug=True)