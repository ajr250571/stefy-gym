# middleware.py
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import auth
from django.utils.deprecation import MiddlewareMixin


class AutoLogoutMiddleware(MiddlewareMixin):

    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        try:
            last_activity = request.session['last_activity']
            last_activity = datetime.strptime(
                last_activity, "%Y-%m-%d %H:%M:%S")

            if datetime.now() - last_activity > timedelta(seconds=settings.SESSION_COOKIE_AGE):
                auth.logout(request)
                del request.session['last_activity']
                return
        except KeyError:
            pass

        request.session['last_activity'] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S")
