# -*- coding: utf-8 -*-

""" A Pyramid app that demonstrates various Deform widgets and
capabilities and which provides a functional test suite  """

import decimal
import inspect
import random
import re
import sys
import csv
import pprint
import logging
import models

from deform.renderer import configure_zpt_renderer

log = logging.getLogger(__name__)

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from colander import iso8601

PY3 = sys.version_info[0] == 3

if PY3:
    def unicode(val, encoding='utf-8'):
        return val

from pkg_resources import resource_filename

from pyramid.config import Configurator
from pyramid.renderers import get_renderer
from pyramid.i18n import get_localizer
from pyramid.i18n import get_locale_name
from pyramid.i18n import TranslationStringFactory
from pyramid.response import Response
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.threadlocal import get_current_request
from pyramid.view import (
    view_config,
    view_defaults,
    )

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer
import sqlahelper
import deform
import colander


DBSession = sqlahelper.get_session()

_ = TranslationStringFactory('deformdemo')

formatter = HtmlFormatter(nowrap=True)
css = formatter.get_style_defs()

# the zpt_renderer above is referred to within the demo.ini file by dotted name

class demonstrate(object):
    def __init__(self, title):
        self.title = title

    def __call__(self, method):
        method.demo = self.title
        return method


# Py2/Py3 compat
# http://stackoverflow.com/a/16888673/315168
# eliminate u''
def my_safe_repr(object, context, maxlevels, level):
    if type(object) == unicode:
        object = object.encode("utf-8")
    return pprint._safe_repr(object, context, maxlevels, level)


@view_defaults(route_name='deformdemo')
class DeformDemo(object):
    def __init__(self, request):
        self.request = request
        self.macros = get_renderer('templates/main.pt').implementation().macros

    def render_form(self, form, appstruct=colander.null, submitted='submit',
                    success=None, readonly=False, is_i18n=False):

        captured = None
        if submitted in self.request.POST:
            # the request represents a form submission
            try:
                # try to validate the submitted values
                controls = self.request.POST.items()
                captured = form.validate(controls)
                if success:
                    response = success()
                    if response is not None:
                        return response
                html = form.render(captured)
            except deform.ValidationFailure as e:
                # the submitted values could not be validated
                html = e.render()

        else:
            # the request requires a simple form rendering
            html = form.render(appstruct, readonly=readonly)

        if self.request.is_xhr:
            return Response(html)

        code, start, end = self.get_code(2)
        locale_name = get_locale_name(self.request)

        reqts = form.get_widget_resources()

        printer = pprint.PrettyPrinter(width=1)
        printer.format = my_safe_repr
        output = printer.pformat(captured)
        captured = highlight(output,
                             PythonLexer(),
                             formatter)

        # values passed to template for rendering
        return {
            'form':html,
            'captured': captured,
            'code': code,
            'start':start,
            'end':end,
            'is_i18n':is_i18n,
            'locale': locale_name,
            'demos':self.get_demos(),
            'title':self.get_title(),
            'css_links':reqts['css'],
            'js_links':reqts['js'],
            }

    def get_code(self, level):
        frame = sys._getframe(level)
        lines, start = inspect.getsourcelines(frame.f_code)
        end = start + len(lines)
        code = ''.join(lines)
        if not PY3:
            code = unicode(code, 'utf-8')
        return highlight(code, PythonLexer(), formatter), start, end

    @view_config(name='thanks.html')
    def thanks(self):
        return Response(
            '<html><body><p>Thanks!</p><small>'
            '<a href="..">Up</a></small></body></html>')

    @view_config(name='allcode', renderer='templates/code.pt')
    def allcode(self):
        params = self.request.params
        start = params.get('start')
        end = params.get('end')
        hl_lines = None
        if start and end:
            start = int(start)
            end = int(end)
            hl_lines = list(range(start, end))
        code = open(inspect.getsourcefile(self.__class__), 'r').read()
        code = code.encode('utf-8')
        formatter = HtmlFormatter(linenos='table', lineanchors='line',
                                  cssclass="hightlight ",
                                  hl_lines=hl_lines)
        html = highlight(code, PythonLexer(), formatter)
        return {'code':html, 'demos':self.get_demos()}

    def get_title(self):
        # gross hack; avert your eyes
        frame = sys._getframe(3)
        attr = frame.f_locals['attr']
        inst = frame.f_locals['inst']
        method = getattr(inst, attr)
        return method.demo

    @view_config(name='pygments.css')
    def cssview(self):
        response = Response(body=css, content_type='text/css')
        response.cache_expires = 360
        return response

    @view_config(renderer='templates/index.pt')
    def index(self):
        return {
            'demos':self.get_demos(),
            }

    def get_demos(self):
        def predicate(value):
            if getattr(value, 'demo', None) is not None:
                return True
        demos = inspect.getmembers(self, predicate)
        L = []
        for name, method in demos:
            url = self.request.resource_url(
                self.request.root, name, route_name='deformdemo')
            L.append((method.demo, url))
        L.sort()
        return L

    
    @view_config(renderer='templates/form.pt', name='checkbox')
    @demonstrate('Checkbox Widget')
    def checkbox(self):

        class Schema(colander.Schema):
            want = colander.SchemaNode(
                colander.Boolean(),
                description='Check this box!',
                widget=deform.widget.CheckboxWidget(),
                title='I Want It!')

        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))

        return self.render_form(form)
	"""
        Source code:

        https://github.com/Pylons/deformdemo/blob/master/deformdemo/templates/popup_example.pt

        https://github.com/Pylons/deformdemo/blob/master/deformdemo/custom_widgets/modal.pt
        """

        class Schema(colander.Schema):

            title = "Pop up example title"

            # Override default form.pt for rendering <form>
            widget = deform.widget.FormWidget(template="modal.pt")

            name = colander.SchemaNode(
                colander.String(),
                description='Enter your name (required)')

        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))

        # CSS is used in <button> opener and JS code
        form.formid = "my-pop-up"

    @view_config(renderer='templates/form.pt', name='edit')
    @demonstrate('Patients')
    def edit(self):
        import datetime

        class Mapping(colander.Schema):
            name = colander.SchemaNode(
                colander.String(),
                description='Content name')
            date = colander.SchemaNode(
                colander.Date(),
                widget=deform.widget.DatePartsWidget(),
                description='Content date')

        class Schema(colander.Schema):
            number = colander.SchemaNode(
                colander.Integer())
            mapping = Mapping()

        schema = Schema()
        form = deform.Form(schema, buttons=('submit',))
        # We don't need to suppy all the values required by the schema
        # for an initial rendering, only the ones the app actually has
        # values for.  Notice below that we don't pass the ``name``
        # value specified by the ``Mapping`` schema.
        appstruct = {
            'number': 42,
            'mapping': {
                'date': datetime.date(2010, 4, 9),
                }
            }

        return self.render_form(form, appstruct=appstruct)
def main(global_config, **settings):
    # paster serve entry point
    settings['debug_templates'] = 'true'

    session_factory = UnencryptedCookieSessionFactoryConfig('seekrit!')
    config = Configurator(settings=settings, session_factory=session_factory)
    config.add_translation_dirs(
        'colander:locale',
        'deform:locale',
        'deformdemo:locale'
        )

    config.include('pyramid_chameleon')

    #
    # Set up Chameleon templates (ZTP) rendering paths
    #

    def translator(term):
        # i18n localizing function
        return get_localizer(get_current_request()).translate(term)

    # Configure renderer
    configure_zpt_renderer(("deformdemo:custom_widgets",), translator)

    config.add_static_view('static_deform', 'deform:static')
    config.add_static_view('static_demo', 'deformdemo:static')
    config.add_route('deformdemo', '*traverse')
    def onerror(*arg):
        pass
    config.scan('deformdemo', onerror=onerror)
    return config.make_wsgi_app()
