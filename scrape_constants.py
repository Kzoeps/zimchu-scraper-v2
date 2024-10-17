"""
Data → node →group_feed → edges[0] →node → comet_sections → content → story →comet_sections →context_layout →story →comet_sections → metadata[0] →story →creation_time

Data → node → comet_sections → content →story →comet_sections →context_layout →story →comet_sections → metadata[0] → story →creation_time
"""
CREATION_TIME_OG = "data.node.group_feed.edges[0].node.comet_sections.content.story.comet_sections.context_layout.story.comet_sections.metadata[0].story.creation_time"
CREATION_TIME_SECONDARY = "data.node.comet_sections.content.story.comet_sections.context_layout.story.comet_sections.metadata[0].story.creation_time"

POST_MESSAGE_OG = "data.node.group_feed.edges[0].node.comet_sections.content.story.message.text"
POST_MESSAGE_SECONDARY = "data.node.comet_sections.content.story.message.text"

POSTER_URL_OG = "data.node.group_feed.edges[0].node.comet_sections.content.story.actors[0].url"
POSTER_URL_SECONDARY = "data.node.comet_sections.content.story.actors[0].url"

POST_URL_OG = "data.node.group_feed.edges[0].node.comet_sections.content.story.wwwURL"
POST_URL_SECONDARY = "data.node.comet_sections.content.story.wwwURL"

ATTACHMENTS_OG = "data.node.group_feed.edges[0].node.comet_sections.content.story.attachments[0]"
ATTACHMENTS_SECONDARY = "data.node.comet_sections.content.story.attachments[0]"

MAIN_ATTACHMENT_PATH = "styles.attachment.media.photo_image.uri"

SUBATTACHMENTS_OG = "styles.attachment.all_subattachments.nodes"
IMAGE_URI_OG = "media.image.uri"

POST_ID_OG = "data.node.group_feed.edges[0].node.post_id"
POST_ID_SECONDARY = "data.node.post_id"

RENT_A_HOUSE_IN_THIMPHU_BHUTAN = 'https://www.facebook.com/groups/1150322371661229?sorting_setting=CHRONOLOGICAL'