from datetime import datetime
from rest_framework.authentication import TokenAuthentication
from vsf_user.models import TokenControl


class VSFTokenAuthentication(TokenAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    def authenticate_credentials(self, key):

        result = super(VSFTokenAuthentication, self).authenticate_credentials(key)

        tc = TokenControl.objects.get(token=result[1])
        tc.count += 1
        tc.last_used = datetime.now()
        tc.save()

        return result
