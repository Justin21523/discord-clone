"""
Voice Chat Service Module
Handles all voice chat-related business logic
"""

import uuid
from datetime import datetime
from sqlmodel import Session, select
from backend.app.db.models import VoiceSession, VoiceServer, Channel, User


class VoiceChatService:
    @staticmethod
    def create_voice_session(
        session: Session,
        user_id: int,
        channel_id: int
    ) -> VoiceSession:
        """
        Create a new voice session for a user in a channel
        """
        # Generate a unique session ID
        session_id = str(uuid.uuid4())
        
        # Create the voice session
        voice_session = VoiceSession(
            user_id=user_id,
            channel_id=channel_id,
            session_id=session_id
        )
        
        session.add(voice_session)
        session.commit()
        session.refresh(voice_session)
        
        return voice_session

    @staticmethod
    def end_voice_session(
        session: Session,
        session_id: str
    ) -> bool:
        """
        End a voice session by setting disconnected_at and is_active to False
        """
        voice_session = session.exec(
            select(VoiceSession)
            .where(VoiceSession.session_id == session_id)
            .where(VoiceSession.is_active == True)
        ).first()
        
        if not voice_session:
            return False
        
        # Update session to mark as ended
        voice_session.disconnected_at = datetime.utcnow()
        voice_session.is_active = False
        
        session.add(voice_session)
        session.commit()
        
        return True

    @staticmethod
    def get_active_sessions_in_channel(
        session: Session,
        channel_id: int
    ) -> list[VoiceSession]:
        """
        Get all active voice sessions in a specific channel
        """
        return session.exec(
            select(VoiceSession)
            .where(VoiceSession.channel_id == channel_id)
            .where(VoiceSession.is_active == True)
        ).all()

    @staticmethod
    def get_voice_session_by_session_id(
        session: Session,
        session_id: str
    ) -> VoiceSession:
        """
        Get a voice session by its session ID
        """
        return session.exec(
            select(VoiceSession)
            .where(VoiceSession.session_id == session_id)
        ).first()

    @staticmethod
    def get_voice_server_for_channel(
        session: Session,
        channel_id: int
    ) -> VoiceServer:
        """
        Get the voice server assigned to a specific channel
        """
        return session.exec(
            select(VoiceServer)
            .where(VoiceServer.channel_id == channel_id)
        ).first()

    @staticmethod
    def assign_voice_server_to_channel(
        session: Session,
        channel_id: int,
        ip_address: str,
        port: int,
        region: str
    ) -> VoiceServer:
        """
        Assign a voice server to a specific channel
        """
        # Check if a voice server is already assigned to this channel
        existing_server = session.exec(
            select(VoiceServer)
            .where(VoiceServer.channel_id == channel_id)
        ).first()
        
        if existing_server:
            # Update the existing server
            existing_server.ip_address = ip_address
            existing_server.port = port
            existing_server.region = region
            existing_server.is_available = True
            
            session.add(existing_server)
            session.commit()
            session.refresh(existing_server)
            
            return existing_server
        
        # Create a new voice server assignment
        voice_server = VoiceServer(
            channel_id=channel_id,
            ip_address=ip_address,
            port=port,
            region=region
        )
        
        session.add(voice_server)
        session.commit()
        session.refresh(voice_server)
        
        return voice_server