# backend/app/routers/guilds.py
from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

# 使用統一的完整路徑
from backend.app.db.session import get_session
from backend.app.db.models import Guild, User, Channel, GuildMember, Role, Category
from backend.app.schemas import GuildCreate, GuildRead, ChannelRead, CategoryRead
from backend.app.deps import get_current_user

router = APIRouter()

# 1. 建立伺服器 (Create Guild)
@router.post("/", response_model=GuildRead)
def create_guild(
    guild_in: GuildCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # 1. 建立 Guild
    new_guild = Guild(
        name=guild_in.name,
        icon=guild_in.icon,
        owner_id=current_user.id # type: ignore
    )
    session.add(new_guild)
    session.commit()
    session.refresh(new_guild)

    # 2. 自動建立 #general 頻道
    default_channel = Channel(
        name="general",
        type="text",
        guild_id=new_guild.id # type: ignore
    )
    session.add(default_channel)

    # 3. 🔥 自動建立 @everyone 身分組 (基礎身分組)
    everyone_role = Role(
        name="@everyone",
        guild_id=new_guild.id, # type: ignore
        position=0, 
        color="#99aab5",
        is_admin=False
    )
    session.add(everyone_role)
    
    # 4. 🔥 自動將 Owner 加入成員列表 (GuildMember)
    owner_member = GuildMember(
        user_id=current_user.id, # type: ignore
        guild_id=new_guild.id, # type: ignore
        nickname=current_user.username
    )
    # 這裡我們暫時不給 Owner 指派 @everyone，因為邏輯上每個人都隱含擁有 @everyone
    # 如果要建立 Admin Role 也可以在這裡做
    
    session.add(owner_member)
    session.commit()
    
    return new_guild
# 2. 獲取伺服器列表 (List Guilds)
@router.get("/", response_model=List[GuildRead])
def read_guilds(
    skip: int = 0, 
    limit: int = 100,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user) # 🔐 必須登入才看得到
):
    # 查詢當前用戶加入的所有 GuildMember 記錄
    memberships = session.exec(
        select(GuildMember)
        .where(GuildMember.user_id == current_user.id)
    ).all()
    
    guild_ids = [m.guild_id for m in memberships]
    
    if not guild_ids:
        return []

    # 查詢這些 ID 對應的 Guild
    statement = select(Guild).where(Guild.id.in_(guild_ids)).offset(skip).limit(limit)
    guilds = session.exec(statement).all()
    return guilds


# 3. 獲取指定伺服器的頻道列表
@router.get("/{guild_id}/channels", response_model=List[ChannelRead])
def read_guild_channels(
    guild_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # 先檢查伺服器存不存在 (這是好習慣)
    guild = session.get(Guild, guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    # 這裡未來可以加入權限檢查：current_user 有沒有加入這個 guild？
    # 目前先假設所有人都可以看

    # 查詢該 Guild 底下的所有 Channel，包括其分類信息
    statement = select(Channel).where(Channel.guild_id == guild_id).order_by(Channel.position)
    channels = session.exec(statement).all()
    return channels


# 3.1 獲取指定伺服器的頻道和分類列表
@router.get("/{guild_id}/structure", response_model=dict)
def read_guild_structure(
    guild_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # 先檢查伺服器存不存在 (這是好習慣)
    guild = session.get(Guild, guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    # 檢查用戶是否為伺服器成員
    from backend.app.db.models import GuildMember
    membership = session.exec(
        select(GuildMember)
        .where(GuildMember.user_id == current_user.id)
        .where(GuildMember.guild_id == guild_id)
    ).first()

    if not membership:
        raise HTTPException(status_code=403, detail="You are not a member of this server")

    # 查詢該 Guild 底下的所有分類，按位置排序
    categories_statement = select(Category).where(Category.guild_id == guild_id).order_by(Category.position)
    categories = session.exec(categories_statement).all()

    # 查詢該 Guild 底下的所有頻道，按位置排序
    channels_statement = select(Channel).where(Channel.guild_id == guild_id).order_by(Channel.position)
    channels = session.exec(channels_statement).all()

    # 組織返回數據
    categories_data = []
    for category in categories:
        category_dict = {
            "id": category.id,
            "name": category.name,
            "position": category.position,
            "created_at": category.created_at,
            "channels": []
        }

        # 添加屬於此分類的頻道
        for channel in channels:
            if channel.category_id == category.id:
                category_dict["channels"].append({
                    "id": channel.id,
                    "name": channel.name,
                    "type": channel.type,
                    "position": channel.position,
                    "created_at": channel.created_at
                })

        categories_data.append(category_dict)

    # 添加未分類的頻道
    uncategorized_channels = []
    for channel in channels:
        if channel.category_id is None:
            uncategorized_channels.append({
                "id": channel.id,
                "name": channel.name,
                "type": channel.type,
                "position": channel.position,
                "created_at": channel.created_at
            })

    return {
        "categories": categories_data,
        "uncategorized_channels": uncategorized_channels
    }

# --- 新增：更新伺服器 Schema ---
class GuildUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None

# 4. 🔥 更新伺服器 (改名、換圖)
@router.put("/{guild_id}", response_model=GuildRead)
def update_guild(
    guild_id: int,
    guild_update: GuildUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    guild = session.get(Guild, guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    # 權限檢查：只有 Owner 可以改 (之後會有 Permission System 檢查 Admin 權限)
    if guild.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")

    if guild_update.name:
        guild.name = guild_update.name
    if guild_update.icon is not None:
        guild.icon = guild_update.icon
    
    session.add(guild)
    session.commit()
    session.refresh(guild)
    return guild

# 5. 🔥 刪除伺服器
@router.delete("/{guild_id}")
def delete_guild(
    guild_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    guild = session.get(Guild, guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    if guild.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
        
    session.delete(guild)
    session.commit()
    return {"ok": True}