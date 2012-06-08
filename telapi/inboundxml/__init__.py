from xml.sax.saxutils import escape
from new import classobj
from telapi.schema import SCHEMA

class Element(object):
    """Root XML element. Also, base class for all other InboundXML elements"""

    _allowed_attributes = []
    _allowed_children   = []
    _allow_blank        = False

    def __init__(self, *args, **kwargs):
        object.__init__(self)

        self._element_name = self.__class__.__name__.split('.')[-1]
        self._body         = ''
        self._attributes   = {}
        self._children     = []

        for i, arg in enumerate(args):
            if i == 0 and isinstance(arg, str):
                self._body = arg
            elif isinstance(arg, Element):
                self._children.append(arg)

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return str(unicode(self))

    def __unicode__(self):
        attribute_string = ''
        body_string = ''.join([unicode(child) for child in self._children]) or self._body

        if not self._allow_blank and not body_string.strip():
            raise ValueError('The "%s" element cannot be blank!' % 
                self._element_name)

        if len(self._attributes):
            attribute_string = ' ' + ' '.join(['%s="%s"' % (escape(unicode(k)), escape(unicode(v))) 
                for k, v in self._attributes.items()])

        return u"<%s%s>%s</%s>" % (self._element_name, attribute_string, body_string, self._element_name)

    def _ensure_attribute(self, name):
        if name not in self._allowed_attributes:
            raise AttributeError('"%s" is not a valid attribute of the "%s" element!' % 
                (name, self._element_name))

    def _ensure_child(self, name):
        if name not in self._allowed_children:
            raise TypeError('"%s" is not a valid child element of the "%s" element!' % 
                (name, self._element_name))

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            return

        if name == 'body':
            self._body = value
            return

        self._ensure_attribute(name)
        self._attributes[name] = value
            
    def __getattr__(self, name):
        if name == 'body':
            return self._body

        self._ensure_attribute(name)

        if name in self._attributes:
            return self._attributes
        else:
            return None

    def __delattr__(self, name):
        self._ensure_attribute(name)

        if name in self._attributes:
            del self._attributes

    def append(self, child):
        self._ensure_child(child._element_name)
        self._children.append(child)



# Loop through the schema file and dynamically create classes for each element type
for element, properties in SCHEMA['inboundxml']['verbs'].items():
    docstring = """%s element
    -------------------------
    properties: %s
    Nestable children: %s
    More info: %s
    """ % (
        element, 
        map(str, properties['attributes']),
        map(str, properties['nesting']), 
        properties['docs_url']
    )

    element_dict = {
        '_allowed_attributes'   : properties['attributes'],
        '_allowed_children'     : properties['nesting'],
        '_allow_blank'          : properties['blank'],
        '__doc__'               : docstring,
    }
    globals()[str(element)] = classobj(str(element), (Element,), element_dict)


