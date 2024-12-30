from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from ..models import Notification, User
from fastapi import BackgroundTasks
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class NotificationService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")

    async def create_notification(
        self,
        db: Session,
        user_id: int,
        message: str,
        event_type: str,
        document_id: Optional[int] = None
    ) -> Notification:
        """Create a new notification."""
        notification = Notification(
            user_id=user_id,
            message=message,
            event_type=event_type,
            document_id=document_id,
            created_at=datetime.utcnow(),
            read=False
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    async def mark_as_read(self, db: Session, notification_id: int) -> Notification:
        """Mark a notification as read."""
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if notification:
            notification.read = True
            notification.read_at = datetime.utcnow()
            db.commit()
            db.refresh(notification)
        return notification

    async def get_user_notifications(
        self,
        db: Session,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications for a user."""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.read == False)
        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    async def send_email_notification(
        self,
        background_tasks: BackgroundTasks,
        recipient_email: str,
        subject: str,
        message: str
    ):
        """Send an email notification in the background."""
        background_tasks.add_task(self._send_email, recipient_email, subject, message)

    def _send_email(self, recipient_email: str, subject: str, message: str):
        """Helper method to send emails."""
        if not all([self.smtp_user, self.smtp_password]):
            return

        msg = MIMEMultipart()
        msg['From'] = self.smtp_user
        msg['To'] = recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
        except Exception as e: 
            print(f"Failed to send email: {str(e)}")

notification_service = NotificationService()
