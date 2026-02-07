
class Node:
    def execute(self, action, **kwargs):
        return {"status": "success", "message": f"Executed {action} with {kwargs}"}
