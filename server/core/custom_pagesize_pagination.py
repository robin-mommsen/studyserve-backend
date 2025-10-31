from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError

class CustomPageSizePagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    allowed_page_sizes = [25, 50, 75, 100]

    def get_page_size(self, request):
        raw_page_size = request.query_params.get(self.page_size_query_param)
        if raw_page_size is not None:
            try:
                raw_page_size = int(raw_page_size)
            except ValueError:
                raise ValidationError({
                    "page_size": "Page size must be an integer"
                })
            if raw_page_size not in self.allowed_page_sizes:
                raise ValidationError({
                    "page_size": f"Invalid page size. Allowed values are: {self.allowed_page_sizes}"
                })
        return super().get_page_size(request)