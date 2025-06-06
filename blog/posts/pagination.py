from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class BlogPostPagination(PageNumberPagination):
    page_size = 5 
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        """
        Customize the pagination response to include more metadata.
        """
        return Response({
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'total_count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })