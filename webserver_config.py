# -*- coding: utf-8 -*-
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Default configuration for the Airflow webserver"""
import os

from airflow.configuration import conf
from flask_appbuilder.security.manager import AUTH_DB, AUTH_OAUTH

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = "acUmM5-5_fsO1eM828BNsDLQaoFw3NUnE3YVjNIM584="  # for CSRF?

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = conf.get('core', 'SQL_ALCHEMY_CONN')

# Flask-WTF flag for cross-site request forgery
WTF_CSRF_ENABLED = True

# ----------------------------------------------------
# AUTHENTICATION CONFIG
# ----------------------------------------------------
# For details on how to set up each of the following authentication, see
# http://flask-appbuilder.readthedocs.io/en/latest/security.html# authentication-methods
# for details.

# The authentication type
AUTH_TYPE = AUTH_OAUTH  #AUTH_DB

# Uncomment to setup Full admin role name
# AUTH_ROLE_ADMIN = 'Admin'

# Uncomment to setup Public role name, no authentication needed
# AUTH_ROLE_PUBLIC = 'Public'

# Will allow user self registration
AUTH_USER_REGISTRATION = True

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "Admin"

azure_authority = "https://login.microsoftonline.com/{0}/oauth2".format(
    os.environ.get("AZURE_TENANT_ID")
)

OAUTH_PROVIDERS = [
    {
        "name": "azure",
        "icon": "fa-windows",
        "token_key": "access_token",
        "remote_app": {
            "consumer_key": os.environ.get("AZURE_APP_ID"),
            "consumer_secret": os.environ.get("AZURE_APP_KEY"),
            "base_url": azure_authority,
            "request_token_params": {
                # NOTE: Adding offline_access or openid seems unnecessary
                "scope": "email profile",  # minimal
                # "scope": "User.read name preferred_username email profile",
                "resource": os.environ.get("AZURE_APP_ID"),
            },
            "request_token_url": None,
            "access_token_url": azure_authority + "/token",
            "authorize_url": azure_authority + "/authorize",
        }
    }
]

# ----------------------------------------------------
# Theme CONFIG
# ----------------------------------------------------

# Flask App Builder comes up with a number of predefined themes
# that you can use for Apache Airflow.
# http://flask-appbuilder.readthedocs.io/en/latest/customizing.html#changing-themes
# Please make sure to remove "navbar_color" configuration from airflow.cfg
# in order to fully utilize the theme. (or use that property in conjunction with theme)
# APP_THEME = "bootstrap-theme.css"  # default bootstrap
# APP_THEME = "amelia.css"
APP_THEME = "cerulean.css" # use to distinguish from prod
# APP_THEME = "cosmo.css"
# APP_THEME = "cyborg.css"
# APP_THEME = "darkly.css"
# APP_THEME = "flatly.css"
# APP_THEME = "journal.css"
# APP_THEME = "lumen.css"
# APP_THEME = "paper.css"
# APP_THEME = "readable.css"
# APP_THEME = "sandstone.css"
# APP_THEME = "simplex.css"
# APP_THEME = "slate.css"
# APP_THEME = "solar.css"
# APP_THEME = "spacelab.css"
# APP_THEME = "superhero.css"
# APP_THEME = "united.css"
# APP_THEME = "yeti.css"
