"""
修复任务#9的平滑轨迹数据

任务#9使用kalman算法运行，但之前有bug没有保存到smoothed_trajectory_results表
此脚本从result_metadata中提取数据并填充到smoothed_trajectory_results表
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置环境变量（使用MySQL配置）
os.environ["DATABASE_URL"] = "mysql+pymysql://root:QWEzxc200348@localhost:3306/rftip"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.error_analysis import ErrorAnalysisTask, SmoothedTrajectoryResult
from app.models.flight_track import RadarStation
from collections import defaultdict
import json

# 数据库连接
DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
Session = sessionmaker(bind=engine)
db = Session()


def fix_task_9():
    """修复任务#9的平滑轨迹数据"""
    # 获取任务#9 - 尝试多种方式查找
    task = db.query(ErrorAnalysisTask).filter(
        ErrorAnalysisTask.task_id == "task_9"
    ).first()

    if not task:
        print("通过task_id 'task_9' 未找到，尝试通过ID=9查找...")
        task = db.query(ErrorAnalysisTask).filter(
            ErrorAnalysisTask.id == 9
        ).first()

    if not task:
        print("任务#9不存在")
        # 列出所有任务供参考
        all_tasks = db.query(ErrorAnalysisTask).all()
        print(f"\n数据库中共有 {len(all_tasks)} 个任务:")
        for t in all_tasks:
            print(f"  ID={t.id}, task_id={t.task_id}, algorithm={t.algorithm_name}, status={t.status}")
        return

    print(f"找到任务: {task.task_id}")
    print(f"算法: {task.algorithm_name}")
    print(f"状态: {task.status}")
    print(f"雷达站: {task.radar_station_ids}")
    print(f"轨迹: {task.track_ids}")

    # 检查result_metadata
    metadata = task.result_metadata
    if not metadata:
        print("\nresult_metadata为空，无法修复")
        return

    print(f"\nresult_metadata keys: {list(metadata.keys()) if isinstance(metadata, dict) else 'Not a dict'}")

    # 检查是否有smoothed_trajectory
    smoothed_trajectory = metadata.get("smoothed_trajectory") if isinstance(metadata, dict) else None
    if not smoothed_trajectory:
        print("result_metadata中没有smoothed_trajectory数据")
        return

    print(f"\nsmoothed_trajectory点数: {len(smoothed_trajectory)}")

    # 按(station_id, batch_id)分组
    trajectories_by_key = defaultdict(list)
    for point in smoothed_trajectory:
        key = (point.get("station_id"), point.get("batch_id", "unknown"))
        trajectories_by_key[key].append(point)

    print(f"轨迹组数: {len(trajectories_by_key)}")

    # 获取雷达站映射
    station_names = {}
    for sid in set(k[0] for k in trajectories_by_key.keys()):
        station = db.query(RadarStation).filter(RadarStation.id == sid).first()
        if station:
            station_names[sid] = station.description or station.station_id or f"站{sid}"
        else:
            station_names[sid] = f"站{sid}"

    # 获取误差统计
    errors = metadata.get("errors", {}) if isinstance(metadata, dict) else {}

    # 创建SmoothedTrajectoryResult记录
    for (station_id, batch_id), points in trajectories_by_key.items():
        # 检查是否已存在
        existing = db.query(SmoothedTrajectoryResult).filter(
            SmoothedTrajectoryResult.task_id == task.task_id,
            SmoothedTrajectoryResult.station_id == station_id,
            SmoothedTrajectoryResult.batch_id == batch_id
        ).first()

        if existing:
            print(f"跳过已存在的记录: station_id={station_id}, batch_id={batch_id}")
            continue

        # 分离原始点和平滑点
        original_points = []
        smoothed_points = []

        for p in points:
            smoothed_points.append({
                "timestamp": p.get("timestamp"),
                "longitude": p.get("longitude"),
                "latitude": p.get("latitude"),
                "altitude": p.get("altitude"),
                "covariance_trace": p.get("covariance_trace"),
            })
            original_points.append({
                "longitude": p.get("orig_lon"),
                "latitude": p.get("orig_lat"),
                "altitude": p.get("orig_alt"),
            })

        # 获取该站点的RMSE
        station_errors = errors.get(station_id, {}) if isinstance(errors, dict) else {}
        rmse_lat = station_errors.get("azimuth_error", 0.0) if isinstance(station_errors, dict) else 0.0
        rmse_lon = station_errors.get("range_error", 0.0) / 111000 if isinstance(station_errors, dict) else 0.0
        rmse_alt = station_errors.get("elevation_error", 0.0) if isinstance(station_errors, dict) else 0.0

        record = SmoothedTrajectoryResult(
            task_id=task.task_id,
            station_id=station_id,
            batch_id=batch_id,
            original_trajectory=original_points,
            smoothed_trajectory=smoothed_points,
            rmse_lat=rmse_lat,
            rmse_lon=rmse_lon,
            rmse_alt=rmse_alt,
            point_count=len(points),
            process_noise=metadata.get("process_noise") if isinstance(metadata, dict) else None,
            measurement_noise=metadata.get("measurement_noise") if isinstance(metadata, dict) else None,
        )
        db.add(record)
        print(f"添加记录: station_id={station_id}, batch_id={batch_id}, 点数={len(points)}")

    db.commit()
    print("\n修复完成!")

    # 验证
    count = db.query(SmoothedTrajectoryResult).filter(
        SmoothedTrajectoryResult.task_id == task.task_id
    ).count()
    print(f"任务#{task.id}的smoothed_trajectory_results记录数: {count}")


if __name__ == "__main__":
    fix_task_9()
