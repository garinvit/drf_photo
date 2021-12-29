from django.http import QueryDict
import json
from rest_framework import parsers
from rest_framework.exceptions import PermissionDenied, NotFound
from django.db import connection, reset_queries
import time
import functools


class MultipartJsonParser(parsers.MultiPartParser):

    def parse(self, stream, media_type=None, parser_context=None):
        result = super().parse(
            stream,
            media_type=media_type,
            parser_context=parser_context
        )
        data = {}
        data = json.loads(result.data["data"])
        qdict = QueryDict('', mutable=True)
        qdict.update(data)
        return parsers.DataAndFiles(qdict, result.files)


class MyMethodsMixin:

    def get_object_from_model(self, model, pk, request):
        try:
            obj = model.objects.get(pk=pk)
            if obj.get_author() != request.user.id:
                raise PermissionDenied({"message": "You don't have permission to access"})
            else:
                return obj
        except model.DoesNotExist:
            raise NotFound({"message": f"{model.__name__} не найден. Укажите правильный id"})

    def filter_queryset(self, queryset, request):
        if queryset:
            model_name = queryset.first().__class__.__name__
        if request.query_params:
            params = request.query_params.get("ordering")
            if params:
                params = params.lower()
            tags = request.query_params.get("tags")
            if tags:
                tags = map(int, tags.split(","))
                for tag in tags:
                    queryset = queryset.filter(tags__id=tag).distinct()
            if params in ["id", "title", "created_at", "-id", "-title", "-created_at"]:
                queryset = queryset.order_by(params)
            elif params in ["count", "-count"] and model_name == "Album":
                if params == "count":
                    queryset = sorted(queryset, key=lambda x: x.get_photo_count())
                else:
                    queryset = sorted(queryset, key=lambda x: x.get_photo_count(), reverse=True)
            elif params in ["album", "-album"] and model_name == "Photo":
                queryset = queryset.order_by(params)
        return queryset


def query_debugger(func):

    @functools.wraps(func)
    def inner_func(*args, **kwargs):

        reset_queries()

        start_queries = len(connection.queries)

        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        end_queries = len(connection.queries)

        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {end_queries - start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        return result

    return inner_func
