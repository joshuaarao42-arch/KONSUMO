from datetime import datetime
from .config import TARIFFS
from .database import connect, init_db

class ValidationError(ValueError): pass
class LookupError(ValueError): pass

def _validate(resource, recorded_at, amount):
    if resource not in TARIFFS: raise ValidationError("resource must be electricity or water")
    try: datetime.fromisoformat(str(recorded_at).replace("Z", "+00:00"))
    except ValueError: raise ValidationError("recorded_at must be a valid date")
    try:
        if float(amount) <= 0: raise ValueError
    except (TypeError, ValueError):
        raise ValidationError("amount must be a number greater than zero")

def add_record(resource, recorded_at, amount, cost=None, notes="", db_path=None, user_id=None):
    if user_id is None: raise ValidationError("An authenticated account is required.")
    init_db(db_path); _validate(resource, recorded_at, amount)
    from .analytics import tiered_cost
    with connect(db_path) as c:
        cur = c.execute(
            "INSERT INTO consumption(user_id,resource,recorded_at,amount,cost,notes) VALUES (?,?,?,?,?,?)",
            (user_id, resource, str(recorded_at), float(amount),
             cost if cost is not None else tiered_cost(float(amount), resource), notes or ""))
        return cur.lastrowid

def get_record(record_id, db_path=None, user_id=None):
    if user_id is None: return None
    init_db(db_path)
    with connect(db_path) as c:
        r = c.execute("SELECT * FROM consumption WHERE id=? AND user_id=?",
                      (record_id, user_id)).fetchone()
        return dict(r) if r else None

def list_records(resource=None, limit=None, offset=0, db_path=None, user_id=None):
    init_db(db_path)
    if user_id is None: return []
    clauses=["user_id=?"]; args=[user_id]
    if resource:
        clauses.append("resource=?"); args.append(resource)
    sql="SELECT * FROM consumption WHERE "+" AND ".join(clauses)+" ORDER BY recorded_at DESC, id DESC"
    if limit is not None: sql += " LIMIT ? OFFSET ?"; args += [limit, offset]
    with connect(db_path) as c:
        return [dict(r) for r in c.execute(sql,args).fetchall()]

def update_record(record_id, db_path=None, user_id=None, **fields):
    if get_record(record_id, db_path, user_id) is None: raise LookupError("record not found")
    _validate(fields["resource"], fields["recorded_at"], fields["amount"])
    with connect(db_path) as c:
        c.execute("""UPDATE consumption SET resource=?,recorded_at=?,amount=?,cost=?,notes=?
                     WHERE id=? AND user_id=?""",
                  (fields["resource"],str(fields["recorded_at"]),float(fields["amount"]),
                   fields.get("cost"),fields.get("notes", ""),record_id,user_id))

def delete_record(record_id, db_path=None, user_id=None):
    if user_id is None: raise LookupError("record not found")
    with connect(db_path) as c:
        if c.execute("DELETE FROM consumption WHERE id=? AND user_id=?",
                     (record_id,user_id)).rowcount == 0:
            raise LookupError("record not found")
