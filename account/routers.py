class DBRouter:
    def db_for_read(self, model, **hints):
        """
        Reads go to read-only mongo.
        """
        if model._meta.model_name == "myuser":
            return "querydb"

        return None

    def db_for_write(self, model, **hints):
        """
        Writes always go to default.
        """
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed in default.
        """
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        All can be migrated into default.
        """
        return None
