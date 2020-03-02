from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordRequestForm
from geoalchemy2.elements import WKTElement
from loguru import logger
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)

from fwas import auth, crud, models, serialize
from fwas.api.dependencies import get_current_user, get_db
from fwas.database import Database
from fwas.serialize import (
    AccessToken,
    AlertIn,
    AlertInDb,
    AlertShareSuccess,
    NotificationOut,
    Token,
    UserIn,
    UserInDb,
    UserOut,
)

router = APIRouter()


@router.get("/ok")
def ok():
    return {"message": "ok"}


@router.post("/auth/token", response_model=AccessToken)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Database = Depends(get_db)
):
    user = await authenticate_user_by_email_password(
        db, form_data.username, form_data.password
    )

    if user is None:
        logger.warning(f"Authentication failed for {form_data.username}: {user}")
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth.get_auth_token(user.id)

    return {"access_token": token, "token_type": "bearer"}


async def authenticate_user_by_email_password(
    db: Database, email: str, password: str
) -> Optional[UserInDb]:
    user = await crud.get_user_by_identity(db, email)

    if user is not None and auth.authenticated(user.password, password=password):
        return user


@router.post("/auth/register", response_model=UserOut)
async def create_user(info: UserIn, db: Database = Depends(get_db)):
    if await crud.get_user_by_username(db, info.username) is not None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Username is taken."
        )

    if await crud.get_user_by_email(db, info.email) is not None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Email is already registered."
        )

    info.password = auth.encrypt_password(info.password)
    user_id = await crud.create_user(db, info)
    user = await crud.get_user(db, user_id)
    user = user.dict()
    user["token"] = auth.generate_auth_token(user_id)

    return user


@router.get("/me", response_model=UserOut)
def user(db: Database = Depends(get_db), user: UserInDb = Depends(get_current_user)):
    """Returns the current users' information."""
    return user


@router.get("/alerts", response_model=List[serialize.AlertInDb])
async def user_alerts(
    since: datetime = None,
    db: Database = Depends(get_db),
    user: UserInDb = Depends(get_current_user),
):
    """Returns the current user's alert definitions."""
    alerts = await crud.get_user_alerts(db, user.id, since)

    return alerts


@router.put("/alerts/subscribe/<uuid:alert_uuid>", response_model=AlertShareSuccess)
def register_alert_subscriber(
    alert_uuid: UUID,
    db: Database = Depends(get_db),
    user: UserInDb = Depends(get_current_user),
):
    """Subscribe to an alert created by another user."""
    user_id = user.id

    alert = models.Alert.query.filter_by(uuid=alert_uuid).first()
    if alert is None:
        response = {"status": "fail", "message": f"Alert {alert_uuid} not found."}
        return response, 400

    if user_id == alert.user_id:
        response = {
            "status": "fail",
            "message": f"{user_id} created the alert and cannot also be a subscriber.",
        }
        return response, 400

    alert.subscribers.append(g.user)

    response = {
        "status": "success",
        "message": "Successfully subscribed to alert.",
    }
    return response, 200


@router.post("/alerts")
def create_alert(
    alert: AlertIn,
    db: Database = Depends(get_db),
    user: UserInDb = Depends(get_current_user),
):
    """Create an alert definition."""
    user = g.user
    data = kwargs
    errors = serialize.new_alert_schema.validate(data)
    if errors:
        current_app.logger.warning(f"Serialization failures: {errors}")
        response = {"status": "fail", "message": str(errors)}
        return response, 400

    try:
        point = WKTElement(f"POINT({data['longitude']} {data['latitude']})", srid=4326)
        alert = models.Alert(user_id=user.id, geom=point, **kwargs)
        alert.save()

        response = {
            "status": "success",
            "message": "Successfully created alert",
            "alert_id": alert.id,
            "alert_uuid": alert.uuid,
        }

        return response, 201
    except Exception:
        current_app.logger.exception("Failed to create alert.")
        response = {
            "status": "fail",
            "message": "Some error occurred. Please try again.",
        }
        return response, 500


@router.get("/notifications", response_model=List[NotificationOut])
async def user_notifications(
    skip: int = 0,
    limit: int = 10,
    db: Database = Depends(get_db),
    user: UserInDb = Depends(get_current_user),
):
    "Returns all notifications generated by alert definitions for this user."
    # TODO (lmalott): add query param to filter based on age of notification
    notifications = await crud.get_user_notifications(db, user.id)

    return notifications
