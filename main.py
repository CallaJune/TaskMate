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
import webapp2
from webapp2_extras import jinja2

from apiclient.discovery import build
from oauth2client.appengine import OAuth2Decorator

import settings

decorator = OAuth2Decorator(client_id=settings.CLIENT_ID,
                            client_secret=settings.CLIENT_SECRET,
                            scope=settings.SCOPE)
service = build('tasks', 'v1')


class MainHandler(webapp2.RequestHandler):

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

class NewHandler(webapp2.RequestHandler):
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

class CreateHandler(webapp2.RequestHandler):
  def render_response(self, template, **context):
    renderer = jinja2.get_jinja2(app=self.app)
    rendered_value = renderer.render_template(template, **context)
    self.response.write(rendered_value)

  @decorator.oauth_aware
  def get(self):  
        template_values = {
        }
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
        print tasks['id']

        '''
        1. Figure out how to insert a task. 
        2. Confirm due date format.
        3. Request due date from user.
        '''

        self.redirect('/')

routes = [
		webapp2.Route('/', MainHandler, name='home'),
    webapp2.Route('/new', NewHandler, name='new'),
    webapp2.Route('/create', CreateHandler, name='create'),
		webapp2.Route(decorator.callback_path, decorator.callback_handler(), name='callback'),
		]

application = webapp2.WSGIApplication(routes, debug=True)