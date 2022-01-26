import ast
import json
import logging

logger = logging.getLogger(__name__)


def str2obj(var):
    """
    Convert string dict/array to an actual dict/array
    this function is used to convert trackdb_configuration
    and trackdb_data from string (as stored in MySQL) to JSON
    (as it need for it to be stored in Elasticsearch when enriching the document)
    :returns: JSON object
    """
    if isinstance(var, dict) or isinstance(var, list):
        return var

    try:
        var = ast.literal_eval(var)
    # if the result of ast.literal_eval is not a dict or array
    # print the error and return None
    except ValueError as ex:
        logger.error(ex)
        return None

    string_var_double_quote = json.dumps(var)
    return json.loads(string_var_double_quote)
