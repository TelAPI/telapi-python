from xml.sax.saxutils import escape

class Response(object):
    """Root XML element. Also, base class for all other TelML elements"""

    _allowed_attributes = []
    _allowed_children = ['Say', 'Play', 'Gather', 'Record', 'Dial']
    _requires_body = False

    def __init__(self, *args, **kwargs):
        object.__init__(self)
        self._element_name = self.__class__.__name__.split('.')[-1]
        self._body = ''
        self._attributes = {}
        self._children = []

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return str(unicode(self))

    def __unicode__(self):
        if self._requires_body and not unicode(self._body).strip():
            raise ValueError('Non-empty "body" property required for the "%s" element!' % self._element_name)

        attribute_string = ''
        body_string = ''.join([unicode(child) for child in self._children]) or self._body

        if len(self._attributes):
            attribute_string = ' ' + ' '.join(['%s="%s"' % (escape(unicode(k)), escape(unicode(v))) for k, v in self._attributes.items()])

        return u"<%s%s>%s</%s>" % (self._element_name, attribute_string, body_string, self._element_name)

    def _ensure_attribute(self, name):
        if name not in self._allowed_attributes:
            raise AttributeError('"%s" is not a valid attribute of the "%s" element!' % (name, self._element_name))

    def _ensure_child(self, name):
        if name not in self._allowed_children:
            raise TypeError('"%s" is not a valid child element of the "%s" element!' % (name, self._element_name))

    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            return

        if name == 'body':
            self._body = value

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

class Say(Response):
    _allowed_children = []
    _allowed_attributes = ['voice', 'loop']
    _requires_body = True

    def __init__(self, body, *args, **kwargs):
        Response.__init__(self, *args, **kwargs)
        self._body = body

class Play(Say):
    _allowed_attributes = ['loop']

class Pause(Response):
    _allowed_children = []
    _allowed_attributes = ['length']

class Gather(Response):
    _allowed_children = ['Say', 'Play', 'Pause']
    _allowed_attributes = ['action', 'method', 'timeout', 'finishOnKey', 'numDigits']

    def __init__(self, *args, **kwargs):
        # TODO: Check if a a child element is required or if gather can sit by itself
        Response.__init__(self, *args, **kwargs)
        
        for child in args:
            self.append(child)

class Record(Response):
    _allowed_children = []
    _allowed_attributes = ['action', 'method', 'timeout', 'finishOnKey', 'transcribe', 'transcribeCallback', 'playBeep', 'bothLegs', 'fileFormat']

class Number(Say):
    _allowed_attributes = ['sendDigits', 'method', 'url']

class Conference(Say):
    _allowed_attributes = ['muted', 'beep', 'startConferenceOnEnter', 'endConferenceOnExit', 'maxParticipants', 'waitUrl', 'waitMethod', 
        'hangupOnStar', 'callbackUrl', 'method', 'waitSound', 'waitSoundMethod', 'digitsMatch', 'stayAlone']

class Dial(Response):
    def __init__(self, body='', *args, **kwargs):
        Response.__init__(self, *args, **kwargs)

        if isinstance(body, Number) or isinstance(body, Conference):
            self._children.append(body)
            self._body = True
        else:
            self._body = body

    _requires_body = True
    _allowed_attributes = ['action', 'method', 'timeout', 'hangupOnStar', 'timeLimit', 'callerId', 'hideCallerId', 'callerName', 'dialMusic', 
    'callbackUrl', 'callbackMethod', 'confirmSound', 'digitsMatch', 'straightToVm', 'heartbeatUrl', 'heartbeatMethod', 'forwardedFrom']
    _allowed_children = ['Number', 'Conference']

