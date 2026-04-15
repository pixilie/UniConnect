import os
import shutil
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.config import settings
from app.core.security import get_current_user
from app.db.database import get_db

resource_router = APIRouter()

os.makedirs(settings.RESOURCES_PATH, exist_ok=True)


@resource_router.post(
    "/groups/{group_id}/resources", response_model=schemas.ResourceResponse
)
async def upload_resource(
    group_id: int,
    title: str = Form(...),
    category: models.ResourceCategory = Form(models.ResourceCategory.OTHER),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail=f"Group {group_id} not found")

    if current_user.role != models.UserRole.ADMIN and group not in current_user.groups:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this group"
        )

    if file.filename:
        file_ext = file.filename.split(".")[-1] if "." in file.filename else "unknown"
        safe_filename = f"{uuid4().hex}.{file_ext}"
        file_path = os.path.join(settings.RESOURCES_PATH, safe_filename)
    else:
        raise HTTPException(
            status_code=500, detail=f"{file.filename} is not a valid filename"
        )

    if title.strip() == "":
        raise HTTPException(
            status_code=422, detail="You can't upload a ressource with an empty title"
        )

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

    new_resource = models.Resource(
        title=title,
        file_path=file_path,
        file_type=file_ext,
        category=category,
        user_id=current_user.id,
        group_id=group_id,
    )
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)

    return new_resource


@resource_router.get(
    "/groups/{group_id}/resources", response_model=list[schemas.ResourceResponse]
)
def get_group_resources(
    group_id: int,
    category: models.ResourceCategory | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if current_user.role != models.UserRole.ADMIN:
        current_group_ids = [g.id for g in current_user.groups]
        if group_id not in current_group_ids:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this group"
            )

    query = db.query(models.Resource).filter(models.Resource.group_id == group_id)

    if category:
        query = query.filter(models.Resource.category == category)

    return query.all()


@resource_router.get("/resources/{resource_id}/download")
def download_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    resource = (
        db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    )
    if not resource:
        raise HTTPException(status_code=404, detail=f"Resource {resource_id} not found")

    if current_user.role != models.UserRole.ADMIN:
        current_group_ids = [g.id for g in current_user.groups]
        if resource.group_id not in current_group_ids:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this resource"
            )

    if not os.path.exists(resource.file_path):
        print("caca")
        raise HTTPException(status_code=404, detail="File missing on the server")

    return FileResponse(
        path=resource.file_path, filename=f"{resource.title}.{resource.file_type}"
    )


@resource_router.patch(
    "/resources/{resource_id}", response_model=schemas.ResourceResponse
)
async def update_resource(
    resource_id: int,
    title: str | None = Form(None),
    category: models.ResourceCategory | None = Form(None),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    resource = (
        db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    )
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    if (
        current_user.role not in [models.UserRole.ADMIN, models.UserRole.TEACHER]
        and resource.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403, detail="Not authorized to update this resource"
        )

    if title is not None:
        resource.title = title
    if category is not None:
        resource.category = category

    if file is not None:
        if file.filename:
            file_ext = (
                file.filename.split(".")[-1] if "." in file.filename else "unknown"
            )
            safe_filename = f"{uuid4().hex}.{file_ext}"
            new_file_path = os.path.join(settings.RESOURCES_PATH, safe_filename)

            try:
                with open(new_file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Could not save new file: {str(e)}"
                )

            if os.path.exists(resource.file_path):
                os.remove(resource.file_path)

            resource.file_path = new_file_path
            resource.file_type = file_ext

        else:
            raise HTTPException(
                status_code=500, detail=f"{file.filename} is an invalid filename"
            )

    db.commit()
    db.refresh(resource)

    return resource


@resource_router.delete(
    "/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    resource = (
        db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    )
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    if (
        current_user.role not in [models.UserRole.ADMIN, models.UserRole.TEACHER]
        and resource.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this resource"
        )

    if os.path.exists(resource.file_path):
        os.remove(resource.file_path)

    db.delete(resource)
    db.commit()

    return None
