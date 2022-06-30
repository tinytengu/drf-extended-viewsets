from functools import wraps
from typing import OrderedDict

from rest_framework import serializers
from rest_framework.request import Request


def extended_route():
    """ Decorator for adding 'extended' query parameter support for ViewSet method. """
    def decorator(function):
        @wraps(function)
        def wrapper(viewset, request: Request, *args, **kwargs):
            # Do nothing fancy if `extended_serializer_class` property of ViewSet is empty.
            if not viewset.extended_serializer_class:
              return function(viewset, request, *args, **kwargs)
          
            # Remember default ViewSet serializer.
            original_serializer = viewset.serializer_class
            # Get serialized result with the default serializer.
            result = function(viewset, request, *args, **kwargs)

            # If ?extended=1 does not appear in request query parameters
            # return default, not extended result.
            if not int(request.query_params.get("extended", 0)):
                return result

            # Parse ?extend_fiels=some,some,some query parameter to specify which exact
            # fields must be extended while the others must remain unextended.
            extend_fields = [
                i for i in request.query_params.get("extend_fields", "").split(",") if i
            ]

            # Override viewset serializer_class to extended serializer class and
            # do serialization with it and then revert back to the original serializer.
            viewset.serializer_class = viewset.extended_serializer_class
            result_extended = function(viewset, request, *args, **kwargs)

            # If there are no extend_fields passed, just return fully extended result
            if not extend_fields:
                return result_extended

            # Otherwise go through every *unextended* serialization result if it's a list or a tuple
            # and replace every key which is specified in extend_fields and replace it with its
            # extended version.
            if isinstance(result.data, (list, tuple)):
                for idx in range(len(result.data)):
                    for ef in extend_fields:
                        if ef in result.data[idx]:
                            result.data[idx][ef] = result_extended.data[idx][ef]
            # Or if serialization result is not an iterable thing just do the same as specified earlier
            # but without iterating over its items.
            elif isinstance(result.data, OrderedDict):
                for ef in extend_fields:
                    if ef in result.data:
                        result.data[ef] = result_extended.data[ef]

            return result

        return wrapper

    return decorator


class ExtendedViewSetMixin:
    """ ExtendedViewSetMixin for adding 'extended' query parameter support for ViewSet.
    Basically, just adds `extended_route` decorator for `retrieve` and `list` methods
    and exposes `extended_serializer_class` property which should be specified in order
    to switch between default and extended serializers.
    """
    extended_serializer_class: serializers.ModelSerializer = None

    @extended_route()
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @extended_route()
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)
