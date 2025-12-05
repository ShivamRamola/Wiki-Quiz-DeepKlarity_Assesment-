from sqlmodel import SQLModel, Field, Column
from typing import Optional, List, Dict, Any
from sqlalchemy import JSON, Text
from datetime import datetime


class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    title: Optional[str] = None
    summary: Optional[str] = None
    key_entities: Optional[Dict[str, Any]] = Field(sa_column=Column(JSON), default={})
    sections: Optional[List[str]] = Field(sa_column=Column(JSON), default=[])
    quiz: Optional[List[Dict[str, Any]]] = Field(sa_column=Column(JSON), default=[])
    related_topics: Optional[List[str]] = Field(sa_column=Column(JSON), default=[])
    raw_html: Optional[str] = Field(sa_column=Column(Text), default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "summary": self.summary,
            "key_entities": self.key_entities,
            "sections": self.sections,
            "quiz": self.quiz,
            "related_topics": self.related_topics,
            "raw_html": self.raw_html,
            "created_at": self.created_at.isoformat(),
        }

    def summary_list(self):
        return {"id": self.id, "url": self.url, "title": self.title, "created_at": self.created_at.isoformat()}
