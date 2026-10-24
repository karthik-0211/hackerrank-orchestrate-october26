"""System Activity Loader.

Loads and indexes system_activity.csv to track deletion worker operations,
retained security audit events, background syncs, exports, and data flow state changes.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ActivityRecord:
    activity_id: str
    event_time: str
    event_type: str
    source_system: str
    target_system: str
    resource_id: str
    reported_result: str
    details: str


class ActivityLoader:
    def __init__(self, dataset_dir: str):
        self.dataset_dir = dataset_dir
        self.activities: List[ActivityRecord] = []
        self.by_resource: Dict[str, List[ActivityRecord]] = {}
        self.by_time: List[ActivityRecord] = []
        self._load_activities()

    def _load_activities(self) -> None:
        activity_file = os.path.join(self.dataset_dir, "system_activity.csv")
        with open(activity_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rec = ActivityRecord(
                    activity_id=row["activity_id"],
                    event_time=row["event_time"],
                    event_type=row["event_type"],
                    source_system=row["source_system"],
                    target_system=row["target_system"],
                    resource_id=row["resource_id"],
                    reported_result=row["reported_result"],
                    details=row["details"],
                )
                self.activities.append(rec)
                self.by_resource.setdefault(rec.resource_id, []).append(rec)

        self.by_time = sorted(self.activities, key=lambda x: x.event_time)

    def get_activities_for_resource(self, resource_id: str) -> List[ActivityRecord]:
        return self.by_resource.get(resource_id, [])

    def get_activities_in_window(self, start_time: str, end_time: str) -> List[ActivityRecord]:
        return [a for a in self.by_time if start_time <= a.event_time <= end_time]
