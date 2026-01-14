import time
from pathlib import Path

class BaseWatcher:
    def __init__(self, vault_path: str, check_interval: int = 120):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Inbox"
        self.check_interval = check_interval
        
        # Ensure the folder exists
        self.needs_action.mkdir(parents=True, exist_ok=True)

    def run(self):
        print(f"Watcher started. Checking every {self.check_interval} seconds...")
        try:
            while True:
                updates = self.check_for_updates()
                for update in updates:
                    self.create_action_file(update)
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            print("Watcher stopped.")

    def check_for_updates(self):
        raise NotImplementedError("Subclasses must implement check_for_updates")

    def create_action_file(self, data):
        raise NotImplementedError("Subclasses must implement create_action_file")