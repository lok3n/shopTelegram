from typing import List
import aiohttp

from shop_yoomoney.exceptions import (
    InvalidRequest,
    UnauthorizedClient,
    InvalidGrant,
    EmptyToken
)


class Authorize:
    def __init__(self, client_id: str, redirect_url: str, client_secret: str, scope: List[str]):
        self.client_id = client_id
        self.redirect_url = redirect_url
        self.client_secret = client_secret
        self.scope = scope
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    async def get_auth_url(self):
        url = "https://yoomoney.ru/oauth/authorize?client_id={client_id}&response_type=code" \
              "&redirect_uri={redirect_uri}&scope={scope}".format(client_id=self.client_id,
                                                                  redirect_uri=self.redirect_url,
                                                                  scope='%20'.join([str(elem) for elem in self.scope]),
                                                                  )

        async with aiohttp.ClientSession(headers=self.headers) as session:
            return await session.post(url)

    async def input_code(self, code: str):
        try:
            code = code[code.index("code=") + 5:].replace(" ", "")
        except:
            pass

        url = "https://yoomoney.ru/oauth/token?code={code}&client_id={client_id}&" \
              "grant_type=authorization_code&redirect_uri={redirect_uri}&client_secret={client_secret}".format(
            code=str(code), client_id=self.client_id, redirect_uri=self.redirect_url, client_secret=self.client_secret)
        async with aiohttp.ClientSession(headers=self.headers) as session:
            response = await session.post(url)
            data = await response.json()

            if "error" in data:
                error = data["error"]
                if error == "invalid_request":
                    raise InvalidRequest()
                elif error == "unauthorized_client":
                    raise UnauthorizedClient()
                elif error == "invalid_grant":
                    raise InvalidGrant()

            if data['access_token'] == "":
                raise EmptyToken()
            return data['access_token']
