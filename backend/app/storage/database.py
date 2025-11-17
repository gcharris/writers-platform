"""Database management for Writers Factory Core."""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager for sessions, results, and analytics."""

    def __init__(self, db_path: str = ".factory/analytics.db"):
        """Initialize database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[sqlite3.Connection] = None

        # Initialize database
        self._init_database()

        logger.info(f"Initialized database at {self.db_path}")

    def _init_database(self) -> None:
        """Initialize database schema."""
        schema_path = Path(__file__).parent / "schema.sql"

        with self.get_connection() as conn:
            with open(schema_path, "r") as f:
                conn.executescript(f.read())
            conn.commit()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self._connection.row_factory = sqlite3.Row

        return self._connection

    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def insert_session(
        self,
        session_id: str,
        workflow_name: str,
        status: str,
        context: Optional[Dict] = None
    ) -> None:
        """Insert a new session.

        Args:
            session_id: Unique session identifier
            workflow_name: Name of workflow
            status: Session status
            context: Session context as dictionary
        """
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO sessions (id, workflow_name, started_at, status, context_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    workflow_name,
                    datetime.now().isoformat(),
                    status,
                    json.dumps(context) if context else None
                )
            )
            conn.commit()

    def update_session(
        self,
        session_id: str,
        status: Optional[str] = None,
        completed_at: Optional[datetime] = None
    ) -> None:
        """Update session status."""
        updates = []
        params = []

        if status:
            updates.append("status = ?")
            params.append(status)

        if completed_at:
            updates.append("completed_at = ?")
            params.append(completed_at.isoformat())

        if not updates:
            return

        params.append(session_id)

        with self.get_connection() as conn:
            conn.execute(
                f"UPDATE sessions SET {', '.join(updates)} WHERE id = ?",
                params
            )
            conn.commit()

    def insert_result(
        self,
        result_id: str,
        session_id: str,
        agent_name: str,
        prompt: str,
        output: str,
        tokens_input: int,
        tokens_output: int,
        cost: float,
        response_time_ms: int,
        model_version: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """Insert a generation result."""
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO results (
                    id, session_id, agent_name, prompt, output,
                    tokens_input, tokens_output, cost, response_time_ms,
                    model_version, metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result_id,
                    session_id,
                    agent_name,
                    prompt,
                    output,
                    tokens_input,
                    tokens_output,
                    cost,
                    response_time_ms,
                    model_version,
                    json.dumps(metadata) if metadata else None
                )
            )
            conn.commit()

    def insert_winner(
        self,
        session_id: str,
        result_id: str,
        reason: Optional[str] = None
    ) -> None:
        """Mark a result as winner."""
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO winners (session_id, result_id, reason)
                VALUES (?, ?, ?)
                """,
                (session_id, result_id, reason)
            )
            conn.commit()

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE id = ?",
                (session_id,)
            )
            row = cursor.fetchone()

            if row:
                return dict(row)

        return None

    def get_session_results(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all results for a session."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM results WHERE session_id = ? ORDER BY created_at",
                (session_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_agent_stats(self, agent_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get agent performance statistics."""
        with self.get_connection() as conn:
            if agent_name:
                cursor = conn.execute(
                    "SELECT * FROM v_agent_performance WHERE agent_name = ?",
                    (agent_name,)
                )
            else:
                cursor = conn.execute("SELECT * FROM v_agent_performance")

            return [dict(row) for row in cursor.fetchall()]

    def get_session_costs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get session cost summary."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM v_session_costs ORDER BY started_at DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_agent_win_rates(self) -> List[Dict[str, Any]]:
        """Get agent win rates."""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM v_agent_win_rates ORDER BY win_rate DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_daily_costs(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily cost summary."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM v_daily_costs LIMIT ?",
                (days,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def cleanup_old_sessions(self, days: int = 90) -> int:
        """Delete sessions older than specified days.

        Args:
            days: Number of days to retain

        Returns:
            Number of sessions deleted
        """
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)

        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                DELETE FROM sessions
                WHERE started_at < datetime(?, 'unixepoch')
                """,
                (cutoff,)
            )
            conn.commit()
            return cursor.rowcount
