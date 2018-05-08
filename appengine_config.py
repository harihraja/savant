# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.appengine.ext import vendor

# Add any libraries installed in the "lib" folder.
vendor.add('lib')

# print os.environ.get('SERVER_SOFTWARE', '') 
 
# if os.environ.get ( 'SERVER_SOFTWARE' , '').startswith('Google App Engine'): 
#     sys.path.insert(0, 'lib.zip') 
# else :
#     if os.name == 'nt' : 
#         os.name = None 
#         sys.platform = '' 