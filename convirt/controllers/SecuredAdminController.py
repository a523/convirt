from tgext.admin import AdminController
from convirt.model.CustomPredicates import is_user

class SecuredAdminController(AdminController):
    allow_only = is_user(u'admin')