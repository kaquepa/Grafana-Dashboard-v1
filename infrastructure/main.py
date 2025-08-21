from infrastructure.database import Database
from infrastructure.models import AdvancedPortManager

db = Database()
porto = AdvancedPortManager(db=db, berths_count=4, tick_seconds=1, new_ship_interval=6)
porto.run()
