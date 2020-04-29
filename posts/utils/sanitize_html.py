import bleach

#: List of allowed tags
ALLOWED_TAGS = [
    *bleach.sanitizer.ALLOWED_TAGS,
    'img',
    'pre',
    'p',
    'span',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'div',
    'br',
    's'
]


#: Map of allowed attributes by tag
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'abbr': ['title'],
    'acronym': ['title'],
    'img': ['src']
}

#: List of allowed styles
ALLOWED_STYLES = []


def sanitize_html(string):
    return bleach.clean(string, ALLOWED_TAGS, ALLOWED_ATTRIBUTES, ALLOWED_STYLES)