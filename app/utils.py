# app/utils.py

from bson import ObjectId

def convert_objectid_to_str(doc):
    """
    Recursively converts all ObjectId instances in a document to strings.

    Parameters:
        doc (dict or list): The document or list of documents to convert.

    Returns:
        dict or list: The converted document with ObjectId fields as strings.
    """
    if isinstance(doc, dict):
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                doc[key] = str(value)
            elif isinstance(value, dict):
                convert_objectid_to_str(value)
            elif isinstance(value, list):
                doc[key] = [convert_objectid_to_str(item) if isinstance(item, (dict, list)) else item for item in value]
    elif isinstance(doc, list):
        doc = [convert_objectid_to_str(item) if isinstance(item, (dict, list)) else item for item in doc]
    return doc
