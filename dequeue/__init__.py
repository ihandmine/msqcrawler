import six
import json

try:
    import cPickle as pickle  # PY2
except ImportError:
    import pickle


class Usage(object):

    @classmethod
    def get(cls, conf, name, default=None):
        """
        :param conf:
        :param name: the setting name
        :type name: string

        :param default: the value to return if no setting is found
        :type default: any
        """
        return conf[name] if conf.get is not None else default

    @classmethod
    def getdict(cls, conf, name, default=None):
        """
        :param conf:
        :param name: the setting name
        :type name: string

        :param default: the value to return if no setting is found
        :type default: any
        """
        value = cls.get(conf, name, default or {})
        if not isinstance(value, six.string_types):
            value = json.loads(value)
        return dict({name: value})

    @classmethod
    def loads(cls, s):
        return pickle.loads(s)

    @classmethod
    def dumps(cls, obj):
        return pickle.dumps(obj, protocol=-1)

