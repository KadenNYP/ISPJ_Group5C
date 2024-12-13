from app.models import ContactMessage
from app.init import db
from datetime import datetime, timedelta, timezone
import uuid


def anonymize_old_records():
    retention_period = 40
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_period)

    old_messages = ContactMessage.query.filter(
        ContactMessage.created_at < cutoff_date,
        ContactMessage.anonymized_at.is_(None)
    ).all()

    for message in old_messages:
        generic_id = str(uuid.uuid4())[:8]
        message.name = f"{generic_id}"
        message.email = f"{generic_id}@gmail.com"
        message.anonymized_at = datetime.now(timezone.utc)

        db.session.add(message)

    db.session.commit()
