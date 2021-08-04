from flask import jsonify, session
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)


import utils.config_handler

def verify_password(username_or_token, password , client_ip, request , g ):
	SECRETS_CONFIG = utils.config_handler.load_json_config()['secrets']
	SECRET_KEY = SECRETS_CONFIG['secret_app']

	if ((password == "") or (password is None)):
		s = Serializer(SECRET_KEY)
		try:
			data = s.loads(username_or_token)
			g.user_id = data['id']
		except SignatureExpired:
			return False # valid token, but expired
		except BadSignature:
			return False # invalid token
		except Exception as e:
			return False
		return True
	else:
		if (str(username_or_token) == SECRETS_CONFIG['api_username']) and (str(password) == SECRETS_CONFIG['api_password']):
			g.user_id = 1 #Unique !
			return True
		else:
			return False


def get_auth_token(g):
	SERVER_CONFIG = utils.config_handler.load_json_config()
	SECRET_KEY = SERVER_CONFIG['secrets']['secret_app']
	TOKEN_EXPIRATION_SECS = int(SERVER_CONFIG['api_configs']['token_expiration_h']) * 3600

	s = Serializer(SECRET_KEY, expires_in = int(TOKEN_EXPIRATION_SECS))
	token = s.dumps({ 'id': g.user_id })
	return jsonify({ 'token': token.decode('ascii') })	


