import unittest

class TestChameleonZPTTemplateLoader(unittest.TestCase):
    def _makeOne(self, **kw):
        from deform.template import ChameleonZPTTemplateLoader
        return ChameleonZPTTemplateLoader(**kw)

    def test_search_path_None(self):
        loader = self._makeOne()
        self.assertEqual(loader.search_path, [])

    def test_search_path_string(self):
        loader = self._makeOne(search_path='path')
        self.assertEqual(loader.search_path, ['path'])

    def test_load_exists(self):
        import os
        fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')
        loader = self._makeOne(search_path=[fixtures])
        result = loader.load('test.pt')
        self.failUnless(result)

    def test_load_notexists(self):
        import os
        from deform.template import TemplateError
        fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')
        loader = self._makeOne(search_path=[fixtures])
        self.assertRaises(TemplateError, loader.load, 'doesnt')
        self.failUnless(
            os.path.join(fixtures, 'doesnt') in loader.notexists)

    def test_load_negative_cache(self):
        import os
        fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')
        path = os.path.join(fixtures, 'test.pt')
        loader = self._makeOne(search_path=[fixtures], auto_reload=True)
        loader.notexists[path] = True
        result = loader.load('test.pt')
        self.failUnless(result)

    def test_load_negative_cache2(self):
        import os
        from deform.template import TemplateError
        fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')
        path = os.path.join(fixtures, 'test.pt')
        loader = self._makeOne(search_path=[fixtures], auto_reload=False)
        loader.notexists[path] = True
        self.assertRaises(TemplateError, loader.load, 'test')

class Test_make_renderer(unittest.TestCase):
    def _callFUT(self, *dirs):
        from deform.template import make_renderer
        return make_renderer(*dirs)

    def test_it(self):
        from pkg_resources import resource_filename
        default_dir = resource_filename('deform', 'tests/fixtures/')
        renderer = self._callFUT(default_dir)
        result = renderer('test', **{})
        self.assertEqual(result, u'<div>Test</div>')

class Test_default_renderer(unittest.TestCase):
    def _callFUT(self, template, **kw):
        from deform.template import default_renderer
        return default_renderer(template, **kw)
    
    def test_call_defaultdir(self):
        result = self._callFUT('checkbox',
                               **{'cstruct':None, 'field':DummyField()})
        self.assertEqual(result,
                         u'<input type="checkbox" name="name" value="true" />')

class DummyWidget(object):
    name = 'name'
    true_val = 'true'
    false_val = 'false'
    
class DummyField(object):
    widget = DummyWidget()
    name = 'name'
    