import importlib
import six
import pkgutil

from importlib import import_module

_ITERABLE_SINGLE_VALUES = dict, six.text_type, bytes


def get_settings(key=None):
    import defaults
    if key:
        if defaults.__dict__.get is not None:
            return defaults.__dict__[key]
        else:
            raise KeyError('[%s] not found in settings' % key)
    return defaults.__dict__


def arg_to_iter(arg):
    if arg is None:
        return []
    elif not isinstance(arg, _ITERABLE_SINGLE_VALUES) and hasattr(arg, '__iter__'):
        return arg
    else:
        return [arg]


def load_object(path):
    """Load an object given its absolute object path, and return it.

    object can be a class, function, variable or an instance.
    path ie: 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware'
    """

    try:
        dot = path.rindex('.')
    except ValueError:
        raise ValueError("Error loading object '%s': not a full path" % path)

    module, name = path[:dot], path[dot+1:]
    mod = import_module(module)

    try:
        obj = getattr(mod, name)
    except AttributeError:
        raise NameError("Module '%s' doesn't define any object named '%s'" % (module, name))

    return obj


def create_instance(objcls, settings, crawler, *args, **kwargs):
    if crawler and hasattr(objcls, 'from_crawler'):
        return objcls.from_crawler(crawler, *args, **kwargs)
    elif hasattr(objcls, 'from_settings'):
        return objcls.from_settings(settings, *args, **kwargs)
    else:
        return objcls(*args, **kwargs)


def load_all_spider(dirname):
    _class_objects = {}

    def load_all_spider_inner(dirname):
        for importer, package_name, ispkg in pkgutil.iter_modules([dirname]):
            if ispkg:
                load_all_spider_inner(dirname + '/' + package_name)
            else:
                module = importer.find_module(package_name)
                module = module.load_module(package_name)
                class_name = module.__dir__()[-1]
                class_object = getattr(module, class_name)
                _class_objects[class_object.spider_name] = class_object

    load_all_spider_inner(dirname)
    return _class_objects.values()

