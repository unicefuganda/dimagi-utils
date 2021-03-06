from time import sleep
from couchdbkit.client import Database
from django.conf import settings
from restkit.errors import RequestFailed

class DesignDoc(object):
    """Data structure representing a design doc"""
    
    def __init__(self, database, id):
        self.id = id
        self._doc = database.get(id)
        self.name = id.replace("_design/", "")
    
    @property
    def views(self):
        views = []
        if "views" in self._doc:
            for view_name, _ in self._doc["views"].items(): 
                views.append(view_name)
        return views

class PerseverentDatabase(object):
    def __init__(self, db):
        self.database = Database(db)
    def __getattr__(self, name):
        if name in ('get', 'save_doc', 'view', 'delete_doc'):
            def _fn(*args, **kwargs):
                try:
                    return getattr(self.database, name)(*args, **kwargs)
                except RequestFailed:
                    sleep(1)
                    _fn(*args, **kwargs)
            return _fn
        else:
            return getattr(self.database, name)

            

def get_db():
    """
    Get the couch database.
    """
    # this is a bit of a hack, since it assumes all the models talk to the same
    # db.  that said a lot of our code relies on that assumption.
    # this import is here because of annoying dependencies

    return PerseverentDatabase(settings.COUCH_DATABASE)


def get_design_docs(database):
    design_doc_rows = database.view("_all_docs", startkey="_design/", 
                                    endkey="_design/zzzz")
    ret = []
    for row in design_doc_rows:
        ret.append(DesignDoc(database, row["id"]))
    return ret

def get_view_names(database):
    design_docs = get_design_docs(database)
    views = []
    for doc in design_docs:
        for view_name in doc.views:
            views.append("%s/%s" % (doc.name, view_name))
    return views