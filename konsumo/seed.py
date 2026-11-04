from datetime import date, timedelta
import random
from .repository import add_record
def seed(db_path, days=425, verbose=True):
    created=0; start=date.today()-timedelta(days=days-1)
    for i in range(days):
        d=(start+timedelta(days=i)).isoformat()
        for resource, base in (("electricity",12),("water",4)):
            add_record(resource,d,round(max(.2,random.gauss(base,base*.15)),3),db_path=db_path); created+=1
    if verbose: print(f"Seeded {created} records")
    return created
