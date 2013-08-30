try:
    import pkg_resources
    VERSION = pkg_resources.require('yacron')[0].version
except:
    VERSION = 'unknown'
