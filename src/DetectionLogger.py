import sqlite3
from pathlib import Path
from datetime import datetime
import cv2


class DetectionLogger:
    """
    Logs detections to a local SQLite database and stores annotated frames on disk.

    Database tables:
      - sessions: one row per app run
      - sources: one row per video source (webcam/file/ip stream)
      - detections: one row per detection event (bbox + confidence + image path)

    Expected detection format:
      detection = {"bbox": (x1, y1, x2, y2), "confidence": float}
    """

    def __init__(self, db_filename="detection_results.db", detections_dir="detections", verbose=False):
        self.db_path = Path(db_filename)
        self.detections_dir = Path(detections_dir)
        self.verbose = verbose

        self.session_id = None
        self.source_id = None

        self.detections_dir.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        """
        Creates a new connection to SQLite.
        Using short-lived connections keeps code simple and avoids dangling connections.
        """
        return sqlite3.connect(str(self.db_path))

    def _init_db(self):
        """
        Creates required tables if they do not exist.
        This is safe to call every time the program starts.
        """
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT NOT NULL,
                    end_time TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    source_type TEXT,
                    source_value TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    session_id INTEGER NOT NULL,
                    source_id INTEGER NOT NULL,
                    label TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    x1 INTEGER NOT NULL,
                    y1 INTEGER NOT NULL,
                    x2 INTEGER NOT NULL,
                    y2 INTEGER NOT NULL,
                    image_path TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions(id),
                    FOREIGN KEY (source_id) REFERENCES sources(id)
                )
                """
            )

    def start_session(self, start_time=None):
        """
        Starts a new session and stores its id in self.session_id.
        """
        start_time = start_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO sessions (start_time) VALUES (?)", (start_time,))
            self.session_id = cur.lastrowid

        if self.verbose:
            print(f"[DB] Session started (ID={self.session_id})")

        return self.session_id

    def end_session(self, end_time=None):
        """
        Closes the current session by writing end_time.
        """
        if not self.session_id:
            return None

        end_time = end_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self._connect() as conn:
            conn.execute("UPDATE sessions SET end_time = ? WHERE id = ?", (end_time, self.session_id))

        ended_id = self.session_id
        self.session_id = None

        if self.verbose:
            print(f"[DB] Session ended (ID={ended_id})")

        return ended_id

    def register_source(self, name, source_type=None, source_value=None):
        """
        Registers the current source and stores its id in self.source_id.
        If the same name was registered before, it reuses the existing row.
        """
        source_value = None if source_value is None else str(source_value)

        with self._connect() as conn:
            cur = conn.cursor()

            cur.execute(
                "INSERT OR IGNORE INTO sources (name, source_type, source_value) VALUES (?, ?, ?)",
                (name, source_type, source_value),
            )

            cur.execute("SELECT id FROM sources WHERE name = ?", (name,))
            row = cur.fetchone()
            self.source_id = row[0] if row else None

        if self.verbose and self.source_id is not None:
            print(f"[DB] Source registered (ID={self.source_id}, Name={name})")

        return self.source_id

    def log_detection(self, annotated_frame, detection, label="Drone"):
        """
        Saves the annotated frame to disk and inserts a detection row in SQLite.

        Returns:
          Absolute image path if logged, otherwise None.
        """
        if not self.session_id or not self.source_id:
            return None

        if not isinstance(detection, dict) or "bbox" not in detection or "confidence" not in detection:
            raise ValueError("detection must be a dict with keys: 'bbox', 'confidence'")

        x1, y1, x2, y2 = map(int, detection["bbox"])
        conf = float(detection["confidence"])

        ts_db = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ts_file = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")

        img_path = self.detections_dir / f"det_s{self.session_id}_src{self.source_id}_{ts_file}.jpg"
        cv2.imwrite(str(img_path), annotated_frame)

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO detections (
                    timestamp, session_id, source_id,
                    label, confidence, x1, y1, x2, y2, image_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (ts_db, self.session_id, self.source_id, label, conf, x1, y1, x2, y2, str(img_path.resolve())),
            )

        return str(img_path.resolve())
