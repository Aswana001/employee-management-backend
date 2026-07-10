from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardResultsSetPagination(PageNumberPagination):
    """
    Standardized Page Number Pagination engine.
    Provides standard 10 records per page limit, allowing dynamic client-side 
    overrides via the 'page_size' query parameter up to a ceiling limit of 100 records.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Overrides the default metadata layout to yield a highly semantic 
        and consistent pagination payload metadata wrap.
        """
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })