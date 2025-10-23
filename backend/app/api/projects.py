"""项目管理API"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.response import success_response, PageResponse
from app.core.exceptions import NotFoundException
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectInDB, ProjectListItem

router = APIRouter()


@router.get("/", response_model=dict)
async def list_projects(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[str] = Query(None, description="项目状态筛选"),
    db: Session = Depends(get_db)
):
    """获取项目列表（分页、搜索）"""
    query = db.query(Project)
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                Project.name.contains(keyword),
                Project.description.contains(keyword)
            )
        )
    
    # 状态筛选
    if status:
        query = query.filter(Project.status == status)
    
    # 按更新时间倒序排列
    query = query.order_by(Project.updated_at.desc())
    
    # 计算总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * page_size
    projects = query.offset(offset).limit(page_size).all()
    
    # 构造响应
    items = [ProjectListItem.model_validate(p) for p in projects]
    page_data = PageResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )
    
    return success_response(data=page_data.model_dump(), message="获取项目列表成功")


@router.get("/{project_id}", response_model=dict)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """获取项目详情"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundException(message=f"项目 ID {project_id} 不存在")
    
    return success_response(
        data=ProjectInDB.model_validate(project).model_dump(),
        message="获取项目详情成功"
    )


@router.post("/", response_model=dict)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db)
):
    """创建新项目"""
    new_project = Project(**project_data.model_dump())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    return success_response(
        data=ProjectInDB.model_validate(new_project).model_dump(),
        message="创建项目成功"
    )


@router.put("/{project_id}", response_model=dict)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db)
):
    """更新项目信息"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundException(message=f"项目 ID {project_id} 不存在")
    
    # 更新字段
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    
    return success_response(
        data=ProjectInDB.model_validate(project).model_dump(),
        message="更新项目成功"
    )


@router.delete("/{project_id}", response_model=dict)
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """删除项目"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundException(message=f"项目 ID {project_id} 不存在")
    
    db.delete(project)
    db.commit()
    
    return success_response(message="删除项目成功")


@router.get("/{project_id}/statistics", response_model=dict)
async def get_project_statistics(project_id: int, db: Session = Depends(get_db)):
    """获取项目统计信息"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFoundException(message=f"项目 ID {project_id} 不存在")
    
    # 构造统计数据
    statistics = {
        "project_id": project.id,
        "project_name": project.name,
        "chapters_count": project.chapters_count,
        "characters_count": project.characters_count,
        "total_duration": project.total_duration,
        "status": project.status,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }
    
    return success_response(data=statistics, message="获取统计信息成功")

