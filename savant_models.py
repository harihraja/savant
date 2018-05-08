from google.appengine.ext import ndb

import logging

class UserAccountInfo(ndb.Model):
    user_id = ndb.StringProperty(required=True)
    user_token = ndb.JsonProperty(compressed=False)

def get_user_ids():

    user_ids = []    
    accounts = UserAccountInfo.query().fetch()
    for account in accounts:
        user_ids.append(account.user_id)

    return user_ids


def store_token(id, token):
    # do not store or update to empty if or refresh token
    if not id or not token:
        return False

    try:
        # look for user id
        accounts = UserAccountInfo.query(UserAccountInfo.user_id == id).fetch()

        # if no entry then create
        if not any(accounts):
            account = UserAccountInfo()
            account.user_id = id            
            account.user_token = token            
            account.put()
            return True

        # update if found and different
        account = accounts[0]
        if account.user_token != token:
            account.user_token = token
            account.put()
    except Exception:
        logging.exception('Exception occured during store_refresh_token.')
        return False

    return True
    

    
def get_token(id):
    try:
        # look for user id    
        accounts = UserAccountInfo.query(UserAccountInfo.user_id == id).fetch()
    except Exception:
        logging.exception('Exception occured during get_refresh_token.')
        return None    

    return accounts[0].user_token if any(accounts) else None