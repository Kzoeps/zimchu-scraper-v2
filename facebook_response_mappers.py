import pydash

from scrape_constants import (
    ATTACHMENTS_OG,
    ATTACHMENTS_SECONDARY,
    CREATION_TIME_OG,
    CREATION_TIME_SECONDARY,
    IMAGE_URI_OG,
    MAIN_ATTACHMENT_PATH,
    POST_ID_OG,
    POST_ID_SECONDARY,
    POST_MESSAGE_OG,
    POST_MESSAGE_SECONDARY,
    POST_URL_OG,
    POST_URL_SECONDARY,
    POSTER_URL_OG,
    POSTER_URL_SECONDARY,
    SUBATTACHMENTS_OG,
)


def get_metric(data, initial_path, secondary_path):
    if pydash.get(data, initial_path):
        return pydash.get(data, initial_path)
    elif pydash.get(data, secondary_path):
        return pydash.get(data, secondary_path)
    else:
        return ""


"""
Get metrics just get the message text from the response.
"""


def get_post_message(data):
    initial_path = POST_MESSAGE_OG
    secondary_path = POST_MESSAGE_SECONDARY
    return get_metric(data, initial_path, secondary_path)


"""posters facebook profile url"""


def get_poster_url(data):
    initial_path = POSTER_URL_OG
    secondary_path = POSTER_URL_SECONDARY
    return get_metric(data, initial_path, secondary_path)


"""post url"""


def get_post_url(data):
    initial_path = POST_URL_OG
    secondary_path = POST_URL_SECONDARY
    return get_metric(data, initial_path, secondary_path)


def get_post_id(data):
    initial_path = POST_ID_OG
    secondary_path = POST_ID_SECONDARY
    return get_metric(data, initial_path, secondary_path)


def get_date_of_posting(data):
    initial_path = CREATION_TIME_OG
    secondary_path = CREATION_TIME_SECONDARY
    return get_metric(data, initial_path, secondary_path)


"""
get images if there are any attached. Only contains like shitty quality thumbnails
using .attachments[0] because only the first one seems to be populated for now
"""


def get_attachments(data):
    if pydash.get(data, ATTACHMENTS_OG):
        main_attachment = get_main_attachment_uri(pydash.get(data, ATTACHMENTS_OG))
        return (
            get_subattachments_uri(pydash.get(data, ATTACHMENTS_OG)) + main_attachment
        )
    elif pydash.get(data, ATTACHMENTS_SECONDARY):
        main_attachment = get_main_attachment_uri(
            pydash.get(data, ATTACHMENTS_SECONDARY)
        )
        return (
            get_subattachments_uri(pydash.get(data, ATTACHMENTS_SECONDARY))
            + main_attachment
        )
    return []


def get_main_attachment_uri(attachment):
    return pydash.get(attachment, MAIN_ATTACHMENT_PATH) or []


def get_subattachments_uri(attachment):
    sub_attachments = pydash.get(attachment, SUBATTACHMENTS_OG) or []
    uris = []
    for sub_attachment in sub_attachments:
        uri = pydash.get(sub_attachment, IMAGE_URI_OG)
        if uri:
            uris.append(pydash.get(sub_attachment, IMAGE_URI_OG))
    return uris
