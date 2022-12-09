"""
:author: Henry Larson
:description: stores and provides authorization credentials for the DVWA webapp.
"""

AUTHS = {'dvwa': ['admin', 'password']}


def get_auth(auth_key):
    """
    Returns login credentials for a given user/pass identifier

    :param auth_key: login identifier
    :return: username and password pair
    """
    # TODO: Handle value retrieval errors
    return AUTHS[auth_key]
