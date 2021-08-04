from flask import jsonify

def flask_response_json(bool_code, response_obj):
    response = {}
    response['response_code'] = bool_code
    response['response_msg'] = response_obj
    return jsonify(response)


def _format_bw_string(input_val):
    if (input_val < 10 * 1024): return str(_format_requests_string(input_val)) +' b'
    if (input_val < 10 * 1024 * 1024): return str(_format_requests_string(int(round(float(input_val/1024))))) +' Kb'
    if (input_val < 10 * 1024 * 1024 * 1024): return str(_format_requests_string(int(round(float(input_val/(1024 * 1024)))))) +' Mb'
    return str(_format_requests_string(int(round(float(input_val/(1024 * 1024 * 1024)))))) +' Gb'


def _format_requests_string(input_val):
    return '{:,}'.format(input_val).replace(',', ' ')