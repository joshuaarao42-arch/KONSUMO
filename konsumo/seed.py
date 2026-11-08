from datetime import date, timedelta
import random
from .repository import add_record

def seed(db_path, days=425, verbose=True, user_id=None):
    if user_id is None:
        raise ValueError("Seeding requires an account ID so sample data stays private.")
    created=0; start=date.today()-timedelta(days=days-1)
    for i in range(days):
        d=(start+timedelta(days=i)).isoformat()
        for resource, base in (("electricity",12),("water",4)):
            add_record(resource,d,round(max(.2,random.gauss(base,base*.15)),3),
                       db_path=db_path,user_id=user_id)
            created+=1
    if verbose: print(f"Seeded {created} records for account {user_id}")
    return created
