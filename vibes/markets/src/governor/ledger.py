"""Durable, atomic reservations. Caps come from the operator's current config."""

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from governor.config import BudgetPolicy, atomic


class LedgerError(RuntimeError):
    pass


@dataclass(frozen=True)
class Reservation:
    status: str
    created: bool
    result: dict


class Ledger:
    def __init__(self, path: Path, policy: BudgetPolicy):
        self.path = path
        self.policy = policy
        self.policy_hash = hashlib.sha256(policy.model_dump_json().encode()).hexdigest()
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._transaction() as db:
            if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
                raise LedgerError("ledger integrity check failed")
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise LedgerError("unsupported ledger schema")
            db.execute("""CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY, task TEXT NOT NULL, policy_hash TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS attempts (
                session_id TEXT NOT NULL REFERENCES sessions(id),
                id TEXT NOT NULL, service TEXT NOT NULL,
                amount INTEGER NOT NULL CHECK(amount > 0),
                status TEXT NOT NULL CHECK(status IN
                    ('RESERVED','AUTHORIZING','SETTLED','RELEASED','DENIED')),
                result TEXT NOT NULL DEFAULT '{}', PRIMARY KEY(session_id, id))""")
            db.execute("""CREATE TABLE IF NOT EXISTS events (
                seq INTEGER PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id),
                time TEXT NOT NULL, kind TEXT NOT NULL, data TEXT NOT NULL)""")
            db.execute("PRAGMA user_version = 1")

    @contextmanager
    def _transaction(self):
        db = sqlite3.connect(self.path, isolation_level=None, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            db.execute("PRAGMA foreign_keys = ON")
            db.execute("PRAGMA synchronous = FULL")
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.execute("COMMIT")
        except BaseException:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def _session(self, db, session_id):
        row = db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not row:
            raise LedgerError("session does not exist; explicitly create a new session")
        if row["policy_hash"] != self.policy_hash:
            raise LedgerError("session policy differs from configuration; refusing to resume")
        return row

    @staticmethod
    def _event(db, session_id, kind, data):
        db.execute(
            "INSERT INTO events(session_id,time,kind,data) VALUES (?,?,?,?)",
            (session_id, datetime.now(UTC).isoformat(), kind, json.dumps(data)),
        )

    def start(self, session_id: str, task: str, *, resume: bool = False) -> None:
        with self._transaction() as db:
            if resume:
                row = self._session(db, session_id)
                if row["task"] != task:
                    raise LedgerError("a session must resume its original task")
            else:
                if db.execute("SELECT 1 FROM sessions WHERE id = ?", (session_id,)).fetchone():
                    raise LedgerError("session already exists; use resume")
                db.execute(
                    "INSERT INTO sessions VALUES (?,?,?)", (session_id, task, self.policy_hash)
                )
            self._event(db, session_id, "SESSION_RESUMED" if resume else "SESSION_CREATED", {})

    def task(self, session_id: str) -> str:
        with self._transaction() as db:
            return self._session(db, session_id)["task"]

    def _snapshot(self, db, session_id):
        self._session(db, session_id)
        rows = db.execute(
            "SELECT status, SUM(amount) AS total FROM attempts WHERE session_id=? GROUP BY status",
            (session_id,),
        ).fetchall()
        totals = {row["status"]: row["total"] for row in rows}
        settled = totals.get("SETTLED", 0)
        held = totals.get("RESERVED", 0) + totals.get("AUTHORIZING", 0)
        available = self.policy.session_cap - settled - held
        if available < 0:
            raise LedgerError("ledger exposure exceeds configured budget")
        return {
            "session_cap": str(self.policy.session_cap),
            "per_call_cap": str(self.policy.per_call_cap),
            "settled": str(settled),
            "held": str(held),
            "available": str(available),
            "unit": "atomic_usdc",
            "payment_mode": "mock",
        }

    def snapshot(self, session_id: str) -> dict:
        with self._transaction() as db:
            return self._snapshot(db, session_id)

    def reserve(self, session_id: str, attempt_id: str, service: str, amount: str) -> Reservation:
        units = atomic(amount)
        if units == 0:
            raise ValueError("paid reservations must have a positive amount")
        with self._transaction() as db:
            snapshot = self._snapshot(db, session_id)
            previous = db.execute(
                "SELECT * FROM attempts WHERE session_id=? AND id=?", (session_id, attempt_id)
            ).fetchone()
            if previous:
                if previous["service"] != service or previous["amount"] != units:
                    raise LedgerError("attempt identity reused with different payment terms")
                return Reservation(previous["status"], False, json.loads(previous["result"]))
            reason = None
            if units > self.policy.per_call_cap:
                reason = "PER_CALL_CAP_EXCEEDED"
            elif units > int(snapshot["available"]):
                reason = "SESSION_CAP_EXCEEDED"
            status = "DENIED" if reason else "RESERVED"
            result = {"code": reason} if reason else {}
            db.execute(
                "INSERT INTO attempts VALUES (?,?,?,?,?,?)",
                (session_id, attempt_id, service, units, status, json.dumps(result)),
            )
            self._event(
                db,
                session_id,
                status,
                {
                    "attempt_id": attempt_id,
                    "service": service,
                    "amount": amount,
                    "code": reason,
                    "budget": self._snapshot(db, session_id),
                },
            )
            return Reservation(status, True, result)

    def lookup(self, session_id: str, attempt_id: str) -> Reservation | None:
        with self._transaction() as db:
            self._session(db, session_id)
            row = db.execute(
                "SELECT * FROM attempts WHERE session_id=? AND id=?", (session_id, attempt_id)
            ).fetchone()
            return Reservation(row["status"], False, json.loads(row["result"])) if row else None

    def mark_authorizing(self, session_id: str, attempt_id: str) -> None:
        """Durably mark potential signature exposure BEFORE calling the signer."""
        with self._transaction() as db:
            self._snapshot(db, session_id)
            changed = db.execute(
                "UPDATE attempts SET status='AUTHORIZING' "
                "WHERE session_id=? AND id=? AND status='RESERVED'",
                (session_id, attempt_id),
            ).rowcount
            if changed != 1:
                raise LedgerError("attempt is not available for authorization")
            self._event(db, session_id, "AUTHORIZING", {"attempt_id": attempt_id})

    def commit(self, session_id: str, attempt_id: str, actual: str, result: dict) -> None:
        units = atomic(actual)
        mismatch = False
        with self._transaction() as db:
            self._session(db, session_id)
            row = db.execute(
                "SELECT * FROM attempts WHERE session_id=? AND id=?", (session_id, attempt_id)
            ).fetchone()
            if not row or row["status"] not in ("AUTHORIZING", "SETTLED"):
                raise LedgerError("attempt has no outstanding authorization")
            if units != row["amount"]:
                mismatch = True
                self._event(
                    db,
                    session_id,
                    "SETTLEMENT_MISMATCH",
                    {
                        "attempt_id": attempt_id,
                        "reported": actual,
                        "reserved": str(row["amount"]),
                    },
                )
            elif row["status"] != "SETTLED":
                db.execute(
                    "UPDATE attempts SET status='SETTLED', result=? WHERE session_id=? AND id=?",
                    (json.dumps(result), session_id, attempt_id),
                )
                self._event(
                    db,
                    session_id,
                    "SETTLED",
                    {
                        "attempt_id": attempt_id,
                        "amount": actual,
                        "budget": self._snapshot(db, session_id),
                    },
                )
        if mismatch:
            raise LedgerError("settlement amount differs from reservation; hold retained")

    def release_unsigned(self, session_id: str, attempt_id: str, reason: str) -> None:
        """Only an unsigned reservation is safe to release without chain reconciliation."""
        with self._transaction() as db:
            self._session(db, session_id)
            changed = db.execute(
                "UPDATE attempts SET status='RELEASED',result=? "
                "WHERE session_id=? AND id=? AND status='RESERVED'",
                (json.dumps({"code": reason}), session_id, attempt_id),
            ).rowcount
            if changed != 1:
                raise LedgerError("cannot release an authorization that may still settle")
            self._event(
                db,
                session_id,
                "RELEASED",
                {
                    "attempt_id": attempt_id,
                    "reason": reason,
                    "budget": self._snapshot(db, session_id),
                },
            )

    def record(self, session_id: str, kind: str, data: dict) -> None:
        with self._transaction() as db:
            self._session(db, session_id)
            self._event(db, session_id, kind, data)

    def report(self, session_id: str) -> dict:
        with self._transaction() as db:
            snapshot = self._snapshot(db, session_id)
            events = [
                {
                    "seq": row["seq"],
                    "time": row["time"],
                    "kind": row["kind"],
                    "data": json.loads(row["data"]),
                }
                for row in db.execute(
                    "SELECT * FROM events WHERE session_id=? ORDER BY seq", (session_id,)
                )
            ]
            attempts = [
                {
                    "attempt_id": row["id"],
                    "service": row["service"],
                    "amount": str(row["amount"]),
                    "status": row["status"],
                    "result": json.loads(row["result"]),
                }
                for row in db.execute(
                    "SELECT * FROM attempts WHERE session_id=? ORDER BY rowid", (session_id,)
                )
            ]
            return {
                "session_id": session_id,
                "budget": snapshot,
                "attempts": attempts,
                "events": events,
            }
