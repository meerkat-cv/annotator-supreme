from flask import request, abort, session


def parse_content_type(request):
    """
    This function is used to extract the content type from the header.
    """
    try:
        content_type = request.headers['content-type']
    except:
        raise error_views.InvalidParametersError('No Content-Type provided')

    json_type = 'application/json'
    data_type = 'multipart/form-data'
    lower_content_type = content_type.lower()
    if lower_content_type.find(json_type) >= 0:
        return json_type
    elif lower_content_type.find(data_type) >= 0:
        return data_type
    else:
        raise error_views.InvalidParametersError('Invalid Content-Type')


def get_param_from_request(request, label):
    """
    This function is used to extract a field from a POST or GET request.
    
    Returns a tuple with (ok:boolean, error:string, value)
    """
    if request.method == 'POST':
        content_type = parse_content_type(request)
        if content_type == "multipart/form-data":
            if label in request.form:
                return (True, "", request.files[label])
            else:
                return (False, "No "+label+" provided in form-data request", None)
        elif content_type == 'application/json':
            try:
                input_params = request.get_json(True)
            except:
                return (False, 'No valid JSON present', None)

            if label in input_params:
                return (True, "", input_params[label])
            else:
                return (False, "No "+label+" provided in json payload", None)
    elif request.method == 'GET':
        if request.args.get(label) == None:
            return (False, "No "+label+" in GET params", None)
        else:
            return (True, "", request.args.get(label))
    else:
        return (False, "Invalid request method", None)
