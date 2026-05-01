class DecisionService:
    def make(self, state: dict):
        """
        Decide what system should do based on:
        - current intent
        - behavior
        - prediction
        
        Example:
        - struggling -> assist
        - repeated intent -> push solution
        
        Return:
        decision dict
        """
        pass

decision_service = DecisionService()