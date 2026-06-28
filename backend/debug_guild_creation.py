import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from sqlmodel import Session, select, create_engine, SQLModel
from backend.app.db.models import User, Guild, GuildMember, Channel, Role, MemberRoleLink
from backend.app.core.config import settings

# Create database engine
engine = create_engine(settings.DATABASE_URL)

def debug_create_guild():
    with Session(engine) as session:
        # 1. Get or create a test user
        username = "testuser_debug"
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f"Creating test user: {username}")
            user = User(
                email="test_debug@example.com",
                username=username,
                hashed_password="hashed_password_placeholder"
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        
        print(f"Using user: {user.username} (ID: {user.id})")

        # 2. Simulate create_guild logic
        guild_name = "Debug Guild"
        print(f"Attempting to create guild: {guild_name}")
        
        try:
            # Step 1: Create Guild
            new_guild = Guild(
                name=guild_name,
                owner_id=user.id
            )
            session.add(new_guild)
            session.commit()
            session.refresh(new_guild)
            print(f"Guild created with ID: {new_guild.id}")

            # Step 2: Create Default Channel
            default_channel = Channel(
                name="general",
                type="text",
                guild_id=new_guild.id
            )
            session.add(default_channel)
            print("Default channel added to session")

            # Step 3: Create @everyone Role
            everyone_role = Role(
                name="@everyone",
                guild_id=new_guild.id,
                position=0,
                color="#99aab5",
                is_admin=False
            )
            session.add(everyone_role)
            print("@everyone role added to session")
            
            # Step 4: Add Owner as Member
            owner_member = GuildMember(
                user_id=user.id,
                guild_id=new_guild.id,
                nickname=user.username
            )
            session.add(owner_member)
            print("Owner member added to session")

            # Commit everything
            session.commit()
            print("Successfully committed all changes!")
            
            # Clean up (optional, but good for testing)
            # session.delete(new_guild) # Cascades should handle the rest
            # session.commit()
            
        except Exception as e:
            print(f"Error during guild creation: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_create_guild()
