from rest_framework.pagination import PageNumberPagination


class Pagination(PageNumberPagination):
    """Класс пагинации."""
    page_size_query_param = 'limit'
    page_size = 6
