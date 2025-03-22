from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Link
from app.schemas import LinkCreate, LinkUpdate, LinkInfo
from app.utils import generate_short_code
from app.redis_client import redis_client
from app.routers.auth import get_current_user
from datetime import datetime
from fastapi.responses import JSONResponse
from app.models import User
from urllib.parse import urlparse

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def validate_url(url: str) -> str:
    """Ensure URL has proper scheme."""
    parsed = urlparse(url)
    if not parsed.scheme:
        return f"http://{url}"
    return url


@router.post("/links/shorten", response_model=LinkInfo)
def create_short_link(
    link: LinkCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    short_code = generate_short_code()

    if link.custom_alias:
        existing = (
            db.query(Link)
            .filter_by(custom_alias=link.custom_alias)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Custom alias already taken"
            )

    new_link = Link(
        short_code=short_code,
        custom_alias=link.custom_alias,
        original_url=link.original_url,
        user_id=user.id,
        expires_at=link.expires_at
    )
    db.add(new_link)
    db.commit()
    db.refresh(new_link)

    try:
        redis_client.set(
            name=short_code,
            value=link.original_url,
            keepttl=link.expires_at
        )
    except Exception as e:
        print(f"Cache set failed: {e}")

    return new_link


@router.get("/{short_code}")
async def redirect_link(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        original_url = redis_client.get(short_code)
        if original_url:
            link = db.query(Link).filter(
                (Link.short_code == short_code)
            ).first()
            if link:
                link.click_count += 1
                link.last_accessed = datetime.utcnow()
                db.commit()
                return {
                    "original_url": link.original_url,
                    "created_at": link.created_at,
                    "click_count": link.click_count,
                    "last_accessed": link.last_accessed
                }
            return {
                "original_url": original_url,
                "created_at": None,
                "click_count": None,
                "last_accessed": None
            }
    except Exception as e:
        print(f"Cache get failed: {e}")

    link = db.query(Link).filter(
        (Link.short_code == short_code)
    ).first()

    if not link:
        return JSONResponse(
            status_code=404,
            content={"detail": "Not found"}
        )

    if link.expires_at and datetime.utcnow() > link.expires_at:
        return JSONResponse(
            status_code=410,
            content={"detail": "Link expired"}
        )

    try:
        redis_client.set(short_code, link.original_url)
    except Exception as e:
        print(f"Cache set failed: {e}")

    link.click_count += 1
    link.last_accessed = datetime.utcnow()
    db.commit()

    return {
        "original_url": link.original_url,
        "created_at": link.created_at,
        "click_count": link.click_count,
        "last_accessed": link.last_accessed
    }


@router.delete("/links/{short_code}")
def delete_link(
    short_code: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    link = db.query(Link).filter_by(short_code=short_code).first()

    if not link or link.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    db.delete(link)
    db.commit()
    
    try:
        redis_client.delete(short_code)
    except Exception as e:
        print(f"Cache delete failed: {e}")

    return {"detail": "Deleted"}


@router.put("/links/{short_code}", response_model=LinkInfo)
def update_link(
    short_code: str,
    data: LinkUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    link = db.query(Link).filter_by(short_code=short_code).first()

    if not link or link.user_id != user.id:
        raise HTTPException(status_code=403)

    link.original_url = data.original_url
    db.commit()

    try:
        redis_client.set(short_code, link.original_url)
    except Exception as e:
        print(f"Cache set failed: {e}")

    return link


@router.get("/links/{short_code}/stats", response_model=LinkInfo)
def link_stats(
    short_code: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    link = db.query(Link).filter_by(short_code=short_code).first()

    if not link or link.user_id != user.id:
        raise HTTPException(status_code=403)

    return link


@router.get("/{short_code}/info")
async def get_link_info(
    short_code: str,
    db: Session = Depends(get_db)
):
    try:
        link = db.query(Link).filter(
            (Link.short_code == short_code)
        ).first()

        if not link:
            return JSONResponse(
                status_code=404,
                content={"detail": "Not found"}
            )

        return {
            "original_url": link.original_url,
            "created_at": link.created_at,
            "click_count": link.click_count,
            "last_accessed": link.last_accessed,
            "short_code": link.short_code,
            "custom_alias": link.custom_alias
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(e)}"}
        )


@router.get("/links/search")
async def search_by_original_url(
    original_url: str,
    db: Session = Depends(get_db)
):
    try:
        links = db.query(Link).filter(
            Link.original_url.like(f"%{original_url}%")
        ).all()

        if not links:
            return JSONResponse(
                status_code=404,
                content={"detail": "No links found for this URL"}
            )

        return [
            {
                "original_url": link.original_url,
                "short_code": link.short_code,
                "created_at": link.created_at,
                "click_count": link.click_count,
                "last_accessed": link.last_accessed,
                "custom_alias": link.custom_alias
            }
            for link in links
        ]

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(e)}"}
        )
