from flask import Flask, request, redirect, make_response, Blueprint, jsonify
from flask_restful import reqparse, Resource, Api
import os
from dotenv import load_dotenv
import requests_oauthlib
from requests_oauthlib.compliance_fixes import facebook_compliance_fix


FB_CLIENT_ID = os.getenv("FB_CLIENT_ID")
FB_CLIENT_SECRET = os.getenv("FB_CLIENT_SECRET_KEY")

FB_AUTHORIZATION_BASE_URL = "https://www.facebook.com/dialog/oauth"
FB_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"

FB_SCOPE = ["email"]

URL = "https://3.16.197.211"

class Fb_login(Resource):

    def get(self):
        facebook = requests_oauthlib.OAuth2Session(
            FB_CLIENT_ID, redirect_uri = URL + "/fb-callback", scope = FB_SCOPE
        )
        authorization_url, _ = facebook.authorization_url(FB_AUTHORIZATION_BASE_URL)

        return redirect(authorization_url)


class Fb_callback(Resource):

    def get(self):
        facebook = requests_oauthlib.OAuth2Session(
            FB_CLIENT_ID, scope=FB_SCOPE, redirect_uri=URL + "/fb-callback"
        )

        # we need to apply a fix for Facebook here
        facebook = facebook_compliance_fix(facebook)

        facebook.fetch_token(
            FB_TOKEN_URL,
            client_secret=FB_CLIENT_SECRET,
            authorization_response=request.url.replace('http', 'https'),
        )

        # Fetch a protected resource, i.e. user profile, via Graph API
        facebook_user_data = facebook.get(
            "https://graph.facebook.com/me?fields=id,name,email,picture{url}"
        ).json()

        email = facebook_user_data.get("email")
        name = facebook_user_data["name"]
        avatar_url = facebook_user_data.get("picture", {}).get("data", {}).get("url")
        data = {
            'name':name,
            'email':email,
            'picture':avatar_url,
            'provider':"facebook",
            "token": facebook.token["access_token"]
        }
        
        return make_response(jsonify(data), 200)