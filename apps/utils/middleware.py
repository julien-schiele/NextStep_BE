from django.utils import translation


class AcceptLanguageHeaderMiddleware:
    """
    Middleware to activate the language from the Accept-Language header for every request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.headers.get("Accept-Language")
        if lang:
            translation.activate(lang)
        else:
            translation.activate(translation.get_language_from_request(request))

        response = self.get_response(request)

        translation.deactivate()
        return response
