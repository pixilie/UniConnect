import asyncio
from datetime import datetime, timezone

from app import models
from app.db.database import (
    SessionLocal,
)


async def deactivate_expired_polls():
    while True:
        db = SessionLocal()
        try:
            now = datetime.now(timezone.utc)

            expired_polls = db.query(models.Poll).filter(
                models.Poll.is_active,
                models.Poll.expires_at != None,
                models.Poll.expires_at <= now
            ).all()

            if expired_polls:
                for poll in expired_polls:
                    poll.is_active = False

                    total_votes = db.query(models.Vote).filter(models.Vote.poll_id == poll.id).count()

                    results_text = []
                    for choice in poll.choices:
                        vote_count = db.query(models.Vote).filter(models.Vote.choice_id == choice.id).count()
                        percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
                        results_text.append(f"- <strong>{choice.text}</strong>: {vote_count} vote(s) ({percentage:.1f}%)")

                    choices_formatted = "<br>".join(results_text)

                    content_str = (
                        f"The poll '{poll.title}' is now closed.<br><br>"
                        f"<strong>Total Votes:</strong> {total_votes}<br><br>"
                        f"<strong>Results:</strong><br>"
                        f"{choices_formatted}"
                    )

                    new_announcement = models.Announcement(
                        title=f"Results: {poll.title}",
                        content=content_str,
                        sent_at=datetime.now(timezone.utc),
                        user_id=poll.user_id,
                        group_id=poll.group_id,
                        urgent=False
                    )

                    db.add(new_announcement)

            db.commit()

        except Exception as e:
            print(f"Error in background task: {e}")
        finally:
            db.close()

        await asyncio.sleep(60)
