# Copyright 2014 Facebook, Inc.

# You are hereby granted a non-exclusive, worldwide, royalty-free license to
# use, copy, modify, and distribute this software in source code or binary
# form for use in connection with the web services and APIs provided by
# Facebook.

# As with any software that integrates with the Facebook platform, your use
# of this software is subject to the Facebook Developer Principles and
# Policies [http://developers.facebook.com/policy/]. This copyright notice
# shall be included in all copies or substantial portions of the software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
from facebookads.objects import *
from facebookads.api import *
from facebookads.exceptions import *

this_dir = os.path.dirname(__file__)
repo_dir = os.path.join(this_dir, os.pardir, os.pardir)
sys.path.insert(1, repo_dir)

config_file = open(os.path.join(this_dir, 'config.json'))
config = json.load(config_file)
config_file.close()

account_id = config['account_id']
access_token = config['access_token']
app_id = config['app_id']
app_secret = config['app_secret']
page_id = config['page_id']
file_path = config['file_path']

FacebookAdsApi.init(app_id, app_secret, access_token)
api = FacebookAdsApi.get_default_api()

response = api.call(
    'GET',
    'https://graph.facebook.com/' + FacebookAdsApi.API_VERSION + '/me/accounts',
)
data = response.json()['data']

page_token = ''
for page in data:
    if page['id'] == page_id:
        page_token = page['access_token']
        break
if page_token == '':
    raise Exception(
        'Page access token for the page id ' + page_id + ' cannot be found.'
    )

FacebookAdsApi.init(app_id, app_secret, page_token)
api = FacebookAdsApi.get_default_api()

response = api.call(
    'POST',
    'https://graph-video.facebook.com/v2.3/' + page_id + '/videos',
    files={'source': (file_path, 'multipart/form-data')},
)
video_id = response.json()['id']

FacebookAdsApi.init(app_id, app_secret, access_token)
api = FacebookAdsApi.get_default_api()

# _DOC open [CUSTOM_AUDIENCE_CREATE_VIDEO_VIEWS_RETARGET]
# _DOC vars [account_id:s, video_id]
# from facebookads.objects import CustomAudience

lookalike = CustomAudience(parent_id=account_id)
lookalike.update({
    CustomAudience.Field.lookalike_spec: {
        'ratio': 0.01,
        'country': 'US',
        'engagement_specs': [
            {
                'action.type': 'video_view',
                'post': video_id,
            },
        ],
        'conversion_type': 'dynamic_rule',
    },
})

lookalike.remote_create()
print(lookalike)
# _DOC close [CUSTOM_AUDIENCE_CREATE_VIDEO_VIEWS_RETARGET]

lookalike.remote_delete()