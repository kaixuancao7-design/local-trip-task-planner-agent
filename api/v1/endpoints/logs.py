"""日志查询与分析API端点

提供日志查询、分析和统计功能。
"""
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from config.logging_config import logger, performance_monitor
from config.settings import settings

router = APIRouter(prefix="/logs", tags=["日志管理"])


class LogFile(BaseModel):
    """日志文件信息"""
    name: str
    path: str
    size: int
    size_human: str
    modified_time: str
    type: str


class LogEntry(BaseModel):
    """日志条目"""
    timestamp: str
    level: str
    logger: str
    message: str
    module: Optional[str] = None
    function: Optional[str] = None
    line: Optional[int] = None


class LogStats(BaseModel):
    """日志统计信息"""
    total_files: int
    total_size: int
    total_size_human: str
    error_count: int
    warning_count: int
    info_count: int


class PerformanceStats(BaseModel):
    """性能统计信息"""
    operation: str
    count: int
    avg: float
    min: float
    max: float
    total: float


def get_log_dir() -> Path:
    """获取日志目录"""
    project_root = Path(__file__).parent.parent.parent
    return project_root / "logs"


def humanize_size(size: int) -> str:
    """转换文件大小为人类可读格式"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"


@router.get("/files", summary="获取日志文件列表")
async def get_log_files():
    """获取所有日志文件列表"""
    try:
        log_dir = get_log_dir()
        if not log_dir.exists():
            return {"success": True, "files": []}
        
        files = []
        for file_path in log_dir.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                file_type = "json" if file_path.suffix == ".json" else "log"
                
                files.append(LogFile(
                    name=file_path.name,
                    path=str(file_path),
                    size=stat.st_size,
                    size_human=humanize_size(stat.st_size),
                    modified_time=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    type=file_type
                ))
        
        # 按修改时间排序
        files.sort(key=lambda x: x.modified_time, reverse=True)
        
        logger.info(f"查询日志文件列表 - 找到 {len(files)} 个文件")
        return {"success": True, "files": files}
    
    except Exception as e:
        logger.error(f"查询日志文件列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content", summary="查询日志内容")
async def get_log_content(
    filename: str = Query(..., description="日志文件名"),
    level: Optional[str] = Query(None, description="日志级别过滤（DEBUG/INFO/WARNING/ERROR）"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    limit: int = Query(100, description="返回条数限制", ge=1, le=1000),
    offset: int = Query(0, description="偏移量", ge=0)
):
    """查询日志文件内容，支持过滤和分页"""
    try:
        log_dir = get_log_dir()
        file_path = log_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="日志文件不存在")
        
        entries = []
        
        # 读取JSON格式日志
        if file_path.suffix == ".json":
            with open(file_path, "r", encoding="utf-8-sig") as f:
                lines = f.readlines()
                
                # 应用过滤
                filtered_lines = []
                for line in lines:
                    try:
                        entry = json.loads(line.strip())
                        
                        # 级别过滤
                        if level and entry.get("level") != level.upper():
                            continue
                        
                        # 关键词过滤
                        if keyword and keyword.lower() not in entry.get("message", "").lower():
                            continue
                        
                        filtered_lines.append(entry)
                    except:
                        continue
                
                # 分页
                paginated = filtered_lines[offset:offset+limit]
                entries = [LogEntry(**entry) for entry in paginated]
                
                total = len(filtered_lines)
        
        # 读取普通日志文件
        else:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                lines = f.readlines()
                
                filtered_lines = []
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 级别过滤
                    if level and level.upper() not in line:
                        continue
                    
                    # 关键词过滤
                    if keyword and keyword.lower() not in line.lower():
                        continue
                    
                    # 简单解析日志行
                    parts = line.split(" - ", 3)
                    if len(parts) >= 4:
                        filtered_lines.append(LogEntry(
                            timestamp=parts[0],
                            level=parts[2],
                            logger=parts[1],
                            message=parts[3]
                        ))
                    else:
                        filtered_lines.append(LogEntry(
                            timestamp="",
                            level="INFO",
                            logger="",
                            message=line
                        ))
                
                # 分页
                entries = filtered_lines[offset:offset+limit]
                total = len(filtered_lines)
        
        logger.info(f"查询日志内容 - 文件: {filename}, 返回 {len(entries)} 条记录")
        return {
            "success": True,
            "filename": filename,
            "total": total,
            "offset": offset,
            "limit": limit,
            "entries": entries
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询日志内容失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", summary="获取日志统计信息")
async def get_log_stats():
    """获取日志统计信息"""
    try:
        log_dir = get_log_dir()
        if not log_dir.exists():
            return {"success": True, "stats": LogStats(
                total_files=0,
                total_size=0,
                total_size_human="0 B",
                error_count=0,
                warning_count=0,
                info_count=0
            )}
        
        total_size = 0
        total_files = 0
        error_count = 0
        warning_count = 0
        info_count = 0
        
        # 统计文件信息
        for file_path in log_dir.iterdir():
            if file_path.is_file():
                total_files += 1
                total_size += file_path.stat().st_size
                
                # 统计JSON日志中的级别
                if file_path.suffix == ".json":
                    with open(file_path, "r", encoding="utf-8-sig") as f:
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                level = entry.get("level", "")
                                if level == "ERROR":
                                    error_count += 1
                                elif level == "WARNING":
                                    warning_count += 1
                                elif level == "INFO":
                                    info_count += 1
                            except:
                                continue
        
        stats = LogStats(
            total_files=total_files,
            total_size=total_size,
            total_size_human=humanize_size(total_size),
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count
        )
        
        logger.info("查询日志统计信息")
        return {"success": True, "stats": stats}
    
    except Exception as e:
        logger.error(f"查询日志统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance", summary="获取性能统计信息")
async def get_performance_stats():
    """获取性能监控统计信息"""
    try:
        stats_list = []
        
        for operation, metrics in performance_monitor.metrics.items():
            stats = performance_monitor.get_stats(operation)
            if stats:
                stats_list.append(PerformanceStats(
                    operation=operation,
                    **stats
                ))
        
        # 按总耗时排序
        stats_list.sort(key=lambda x: x.total, reverse=True)
        
        logger.info(f"查询性能统计信息 - {len(stats_list)} 个操作")
        return {"success": True, "performance_stats": stats_list}
    
    except Exception as e:
        logger.error(f"查询性能统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/errors/recent", summary="获取最近的错误日志")
async def get_recent_errors(
    hours: int = Query(24, description="查询最近N小时的错误", ge=1, le=168)
):
    """获取最近的错误日志"""
    try:
        log_dir = get_log_dir()
        error_log = log_dir / "error.log"
        
        if not error_log.exists():
            return {"success": True, "errors": []}
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        errors = []
        
        with open(error_log, "r", encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # 解析时间戳
                try:
                    timestamp_str = line.split(" [")[0]
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    
                    if timestamp > cutoff_time:
                        errors.append(line)
                except:
                    continue
        
        # 返回最近100条错误
        errors = errors[-100:]
        
        logger.info(f"查询最近错误日志 - 最近 {hours} 小时, 找到 {len(errors)} 条")
        return {"success": True, "hours": hours, "errors": errors}
    
    except Exception as e:
        logger.error(f"查询最近错误日志失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/files/{filename}", summary="删除日志文件")
async def delete_log_file(filename: str):
    """删除指定的日志文件（仅允许删除备份文件）"""
    try:
        log_dir = get_log_dir()
        file_path = log_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="日志文件不存在")
        
        # 安全检查：不允许删除主日志文件
        main_files = ["app.log", "error.log", "app.json"]
        if filename in main_files:
            raise HTTPException(status_code=403, detail="不允许删除主日志文件")
        
        # 删除文件
        file_path.unlink()
        
        logger.info(f"删除日志文件: {filename}")
        return {"success": True, "message": f"日志文件 {filename} 已删除"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除日志文件失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
