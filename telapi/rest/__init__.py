import os
import sys
import exceptions
import requests
import platform
from new import classobj
import json
from telapi.schema import SCHEMA
from telapi import VERSION



USER_AGENT = "TelAPI-Python/%s (%s %s)" % (VERSION, platform.system(), platform.release())


def _name_to_instance_class_name(resource_name):
    return str(resource_name)

def _name_to_instance_class(resource_name):
    return globals()[_name_to_instance_class_name(resource_name)]

def _name_to_list_class_name(resource_name):
    return str(resource_name) + "ListResource"

def _name_to_list_class(resource_name):
    return globals()[_name_to_list_class_name(resource_name)]



class Resource(object):
    """Base class for InstanceResource and ListResource"""
    def __init__(self, parent):
        self._parent        = parent
        self._full_url      = None
        self._populated     = False
        self._resource_data = None
        self._client        = None

        if parent:
            self._client = parent._client

    def __nonzero__(self):
        return True

    @property
    def _url(self):
        if self._full_url:
            return self._full_url
        else:
            # TODO: Traverse tree upwards
            if not self._parent:
                return self._short_url

            if self._short_url:
                self._full_url = self._parent._url + "/" + self._short_url
            else:
                self._full_url = self._parent._url

            return self._full_url



class ListResourceMetaclass(type):
    def __new__(meta, classname, bases, classDict):
        return type.__new__(meta, classname, bases, classDict)

class ListResource(Resource):
    __metaclass__ = ListResourceMetaclass

    def __init__(self, parent, page=0, page_size=50):
        super(ListResource, self).__init__(parent=parent)
        self.page      = page
        self.page_size = page_size
        self.total     = 0
        self.num_pages = 0
        self.start     = 0
        self.end       = sys.maxint
        self.step      = 1
        self.current   = 0
        self._filters  = {}
        self._total    = None
        

    def __getitem__(self, key):
        # Numeric index
        if isinstance(key, int):
            # TODO: Cache length so it"s not calulated every time

            self.fetch()

            if not self.total:
                raise IndexError()

            resource_list = self._resource_data[self._short_name]

            # Negative index
            if key < 0:
                key = len(resource_list) + key

            nth_item = resource_list[key]

            return _name_to_instance_class(self._name)(parent=self, fetched_data=nth_item)

        # Extended slice
        # Paginate
        elif isinstance(key, slice):
            # TODO: Support negative indexing for slices

            # TODO: Temporarily fetching n results where n is the slice end and then performing the slice
            # It is inefficient since 90:100 will fetch all first 100 rows

            # # Map slice to page & page size e.g. [10:20] -> ?Page=1&PageSize=10
            # # Trouble when it"s not nice and even, such as [15:50] -> ?Page=0&PageSize=50, then we have to slice the results [15:50], discarding the first 15
            #
            # diff = key.stop - key.start
            # if diff < key.start:
            #     page_size = diff
            # else:
            #     page_size = key.start + key.stop

            page = 0
            page_size = key.stop

            # If page & page size are the same, return slice, else return a new list resource
            if self.page == page and self.page_size == page_size:
                indices = key.indices(len(self))

                return [self[i] for i in indices]
            else:
                # The pages are different, so we can"t use the data (if any) already fetched
                paginated_list_resource           = self.copy()
                paginated_list_resource.page      = page
                paginated_list_resource.page_size = page_size
                paginated_list_resource.start     = key.start
                paginated_list_resource.end       = key.stop
                paginated_list_resource.step      = key.step or 1

                return paginated_list_resource

        # Lookup by SID
        else:
            if self._populated:
                for item in self._resource_data[self._short_name]:
                    if item["sid"] == key:
                        return _name_to_instance_class(self._name)(parent=self, fetched_data=item)
            else:
                return _name_to_instance_class(self._name)(parent=self, sid=key)

        return IndexError()

    def __len__(self):
        self.fetch()

        return self._page_end - self._page_start

    def __iter__(self):
        return self

    def next(self):
        current_index = (self.start or 0) + (self.current or 0)

        if current_index >= self.end:
            raise StopIteration()

        try:
            item = self[current_index]
        except IndexError:
            raise StopIteration()

        self.current += self.step

        return item

    def fetch(self, resource_data=None):
        """Populates this class with remote data"""
        if not self._populated:
            params = {
                "Page"      : self.page,
                "PageSize"  : self.page_size,
            }

            params.update(self._filters)

            if not resource_data:
                self._resource_data = self._client._get(self._url + ".json", params)
            else:
                self._resource_data = resource_data

            self.total = self._resource_data["total"]
            self._page_start = self._resource_data["start"]
            self._page_end = self._resource_data["end"]

            self._populated = True

    def copy(self):

        new_copy = _name_to_list_class(self._name)(parent=self._parent)
        new_copy._filters = self._filters.copy()

        return new_copy

    def new(self, **kwargs):
        resource_instance = _name_to_instance_class(self._name)(parent=self, **kwargs)

        return resource_instance

    def create(self, **kwargs):
        resource_instance = self.new(**kwargs)
        resource_instance.save()

        return resource_instance

    def filter(self, **kwargs):
        copy = self.copy()

        for name, value in kwargs.items():
            if name in copy._filter_params:
                copy._filters[name] = value
            else:
                raise AttributeError("%s is not a valid filter for %s" % (name, copy))

        return copy

    def clear(self):
        self._populated = False

        return self

    def __repr__(self):
        self.fetch()
        return str(self._resource_data)




class InstanceResourceMetaclass(type):
    def __new__(meta, classname, bases, classDict):
        return type.__new__(meta, classname, bases, classDict)

class InstanceResource(Resource):
    __metaclass__ = InstanceResourceMetaclass

    def __init__(self, parent, sid=None, fetched_data=None, **kwargs):
        super(InstanceResource, self).__init__(parent=parent)

        for key, value in kwargs.items():
            setattr(self, key, value)

        if 'sid' in self._allowed_attributes:
            self.sid = str(sid).strip() if sid else sid
            self._short_url = self.sid
        else:
            self._short_url = ""

        self._populated = False
        

        # This will be set if a list of objects is fetched, rather than one instance
        if fetched_data:
            self.fetch(resource_data=fetched_data)


    def fetch(self, resource_data=None):
        """Populates this class with remote data"""
        try:
            if not resource_data:
                resource_data = self._client._get(self._url + ".json")

            for name in self._allowed_attributes:
                setattr(self, name, resource_data.get(name, None))

            if 'sid' in self._allowed_attributes:
                self._short_url = self.sid
            else:
                self._short_url = ""

            self._populated = True
            self._resource_data = resource_data
        except exceptions.RequestError, e:
            if not e.http_code == 405:
                print e
                raise

    def __getattr__(self, name):
        if name.startswith('_'):
            return self.__getattribute__(name)

        if name == "from_number":
            name = "from"
        elif name == "to_number":
            name = "to"

        subresource = SCHEMA["rest_api"]["components"].get(name, None)

        if subresource:
            if self._short_name in subresource["parent_resources"]:
                resource_instance = _name_to_list_class(subresource["name"])(parent=self)
                return resource_instance

        if not self._populated:
            self.fetch()

        return self.__getattribute__(name)

    def __setattr__(self, name, value):
        if name == "from_number":
            name = "from"
        elif name == "to_number":
            name = "to"

        if name.startswith('_') or name in self._allowed_attributes or name in self._create_params or name in self._update_params:
            return object.__setattr__(self, name, value)
        
        raise AttributeError("'%s' not a valid attribute of %s (allowed attributes: %s)" % (name, self, self._allowed_attributes))

        

    def save(self):
        data = {}

        if not self._populated:
            for attr, param in self._create_params.items():
                try:
                    attr_value = getattr(self, attr, None)
                    print 'save create', attr, param, attr_value
                    if attr_value is not None:
                        data[param] = attr_value
                except AttributeError:
                    # This is probably an update/create attribute that was not set
                    pass
        else:
            for attr, param in self._update_params.items():
                try:
                    attr_value = getattr(self, attr, None)
                    print 'save update', attr, param, attr_value
                    if attr_value is not None:
                        data[param] = attr_value
                except AttributeError:
                    # This is probably an update/create attribute that was not set
                    pass

        # print 'save data:', data

        resource_data = self._client._post(self._url + ".json", data)
        self._full_url = None
        self.fetch(resource_data=resource_data)

        return self

    def delete(self):
        self._client._delete(self._url + ".json")

        return None

    def __repr__(self):
        self.fetch()
        return str(self._resource_data)




class ClientMetaclass(type):
    def __new__(meta, classname, bases, classDict):
        return type.__new__(meta, classname, bases, classDict)

class Client(object):
    """TelAPI REST Client

    Instead of passing account_sid and auth_token to this class, you can set
    environment variables `TELAPI_ACCOUNT_SID` and `TELAPI_AUTH_TOKEN`.
    """

    __metaclass__ = ClientMetaclass
    
    def __init__(self, account_sid=None, auth_token=None, base_url="https://api.telapi.com/2011-07-01/", *args, **kwargs):
        object.__init__(self)
        self.account_sid = account_sid or os.environ.get("TELAPI_ACCOUNT_SID")
        self.auth_token  = auth_token or os.environ.get("TELAPI_AUTH_TOKEN")
        self.base_url    = base_url

        if not self.account_sid or not self.account_sid.startswith("AC"):
            raise exceptions.AccountSidError()

        if not self.auth_token:
            raise exceptions.AuthTokenError()

    def _send_request(self, resource_uri, method, params=None):
        # print
        # print "_send_request", self.base_url, resource_uri, method, params
        # print

        url = self.base_url + resource_uri
        extra_params = {
            "auth": (self.account_sid, self.auth_token),
            "headers": {
                "Content-Type"  : "application/json",
                "User-Agent"    : USER_AGENT,
            }
        }

        if method == "POST":
            response = requests.post(url, data=params, **extra_params)
        elif method == "DELETE":
            response = requests.delete(url, data=params, **extra_params)
        else:
            response = requests.get(url, params=params, **extra_params)

        if response.status_code >= 400:
                try:
                    error = json.loads(response.content)
                    raise exceptions.RequestError("Error code %s. %s. More info at %s" % (error["code"], error["message"], error["more_info"]), error_code=error["code"], http_code=response.status_code)
                except ValueError:
                    raise exceptions.RequestError("Errror requesting %s to '%s'. Status code: %s" % (method, url, response.status_code), http_code=response.status_code)

        # print
        # print response.content
        # print

        try:
            return json.loads(response.content)
        except ValueError, e:
            print 'Bad JSON returned! response.text:'
            print response.content

            raise
        except:
            print 'Bad Response!'
            print response, dir(response)
            
            raise

    def _get(self, resource_uri, params=None):
        return self._send_request(resource_uri, "GET", params)

    def _post(self, resource_uri, params=None):
        return self._send_request(resource_uri, "POST", params)

    def _delete(self, resource_uri, params=None):
        return self._send_request(resource_uri, "DELETE", params)

    # TODO: Set these attrs with a factory so that they"ll show up in the docstring
    def __getattr__(self, name):
        resource = SCHEMA["rest_api"]["components"].get(name, None)

        # Make sure the resource has no parents (this will be just accounts)
        if not resource or resource["parent_resources"]:
            raise AttributeError()

        # Resolve a name like "accounts" to a list resource
        resource_instance = _name_to_list_class(resource["name"])(parent=None)
        resource_instance._client = self

        return resource_instance

        



# Create Classes for all REST resources dynamically
for element, properties in SCHEMA["rest_api"]["components"].items():

    # Create Instance Resource Class
    class_name = _name_to_instance_class_name(properties["name"])
    docstring = """%s REST instance resource
    -------------------------
    Attributes: %s
    Parent resources: %s
    More info: %s
    """ % (
        element, 
        map(str, properties["attributes"]),
        map(str, properties["parent_resources"]), 
        properties.get("docs_short_url", "")
    )

    resource_dict = {
        "_allowed_attributes"   : properties["attributes"],
        "_parent_resources"     : properties["parent_resources"],
        "_short_url"            : properties["url"],
        "__doc__"               : docstring,
        "_name"                 : properties["name"],
        "_short_name"           : element,
        "_create_params"        : properties.get("create_params", {}),
        "_update_params"        : properties.get("update_params", {}),
    }
    globals()[class_name] = classobj(class_name, (InstanceResource,), resource_dict)


    # Create List Resource Class
    class_name = _name_to_list_class_name(properties["name"])
    docstring = """%s REST list resource
    -------------------------
    Parent resources: %s
    More info: %s
    """ % (
        element, 
        map(str, properties["parent_resources"]), 
        properties.get("docs_url", "")
    )

    resource_dict = {
        "_allowed_attributes"   : properties["attributes"],
        "_parent_resources"     : properties["parent_resources"],
        "_short_url"            : properties["url"],
        "__doc__"               : docstring,
        "_name"                 : properties["name"],
        "_short_name"           : element,
        "_filter_params"        : properties.get("filter_params", []),
        "_fetchable"            : properties.get("fetchable", True)
    }
    globals()[class_name] = classobj(class_name, (ListResource,), resource_dict)





