class PostgresStore:
    def save_event(self, event: dict):
        """
        Insert raw event into DB
        
        Table:
        events(user_id, intent, timestamp)
        
        This is SOURCE OF TRUTH
        """
        pass

postgres_store = PostgresStore()