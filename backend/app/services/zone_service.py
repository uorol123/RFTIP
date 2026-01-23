"""
禁飞区管理服务 - 处理禁飞区创建、入侵检测和邮件预警
"""
import json
import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from core.config import get_settings
from app.models.restricted_zone import RestrictedZone, ZoneIntrusion
from app.models.flight_track import FlightTrackCorrected
from app.schemas.zone import RestrictedZoneCreate, RestrictedZoneUpdate

settings = get_settings()


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    计算两点之间的距离（Haversine 公式）

    Returns:
        距离（米）
    """
    R = 6371000  # 地球半径（米）

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def is_point_in_circle(
    point_lat: float,
    point_lon: float,
    center_lat: float,
    center_lon: float,
    radius: float,
) -> Tuple[bool, float]:
    """
    判断点是否在圆形区域内

    Returns:
        (是否在圆内, 距离边界的距离)
    """
    distance = calculate_distance(point_lat, point_lon, center_lat, center_lon)
    is_inside = distance <= radius
    distance_from_boundary = radius - distance if is_inside else distance - radius
    return is_inside, distance_from_boundary


def is_point_in_polygon(
    point_lat: float,
    point_lon: float,
    vertices: List[Tuple[float, float]]
) -> Tuple[bool, float]:
    """
    判断点是否在多边形内（射线法）

    Returns:
        (是否在多边形内, 到边界的最小距离)
    """
    n = len(vertices)
    inside = False

    # 射线法判断点是否在多边形内
    j = n - 1
    for i in range(n):
        if ((vertices[i][1] > point_lon) != (vertices[j][1] > point_lon)) and \
           (point_lat < (vertices[j][0] - vertices[i][0]) * (point_lon - vertices[i][1]) /
            (vertices[j][1] - vertices[i][1]) + vertices[i][0]):
            inside = not inside
        j = i

    # 计算到边界的最小距离
    min_distance = float('inf')
    for i in range(n):
        j = (i + 1) % n
        dist = point_to_line_distance(
            point_lat, point_lon,
            vertices[i][0], vertices[i][1],
            vertices[j][0], vertices[j][1]
        )
        min_distance = min(min_distance, dist)

    return inside, -min_distance if inside else min_distance


def point_to_line_distance(
    px: float, py: float,
    x1: float, y1: float,
    x2: float, y2: float
) -> float:
    """计算点到线段的距离"""
    A = px - x1
    B = py - y1
    C = x2 - x1
    D = y2 - y1

    dot = A * C + B * D
    len_sq = C * C + D * D

    param = -1
    if len_sq != 0:
        param = dot / len_sq

    if param < 0:
        xx, yy = x1, y1
    elif param > 1:
        xx, yy = x2, y2
    else:
        xx = x1 + param * C
        yy = y1 + param * D

    dx = px - xx
    dy = py - yy
    return math.sqrt(dx * dx + dy * dy)


def create_zone(db: Session, zone_data: RestrictedZoneCreate, user_id: int) -> RestrictedZone:
    """创建禁飞区"""
    zone = RestrictedZone(
        user_id=user_id,
        zone_name=zone_data.zone_name,
        zone_type=zone_data.zone_type,
        coordinates=zone_data.coordinates,
        min_altitude=zone_data.min_altitude,
        max_altitude=zone_data.max_altitude,
        is_active=int(zone_data.is_active),
        notification_email=zone_data.notification_email,
        notification_enabled=int(zone_data.notification_enabled),
        description=zone_data.description,
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


def get_zone_by_id(db: Session, zone_id: int, user_id: Optional[int] = None) -> Optional[RestrictedZone]:
    """根据 ID 获取禁飞区"""
    query = db.query(RestrictedZone).filter(RestrictedZone.id == zone_id)
    if user_id is not None:
        query = query.filter(RestrictedZone.user_id == user_id)
    return query.first()


def get_active_zones(db: Session) -> List[RestrictedZone]:
    """获取所有激活的禁飞区"""
    return db.query(RestrictedZone).filter(
        RestrictedZone.is_active == 1,
        RestrictedZone.zone_type.in_(["circle", "polygon"])
    ).all()


def update_zone(
    db: Session,
    zone_id: int,
    zone_update: RestrictedZoneUpdate,
    user_id: int
) -> Optional[RestrictedZone]:
    """更新禁飞区"""
    zone = get_zone_by_id(db, zone_id, user_id)
    if not zone:
        return None

    update_data = zone_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(zone, field, value)

    zone.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(zone)
    return zone


def delete_zone(db: Session, zone_id: int, user_id: int) -> bool:
    """删除禁飞区"""
    zone = get_zone_by_id(db, zone_id, user_id)
    if not zone:
        return False

    db.delete(zone)
    db.commit()
    return True


def check_intrusion(
    track: FlightTrackCorrected,
    zone: RestrictedZone,
) -> Optional[dict]:
    """
    检查轨迹点是否入侵禁飞区

    Returns:
        如果检测到入侵，返回入侵信息字典；否则返回 None
    """
    # 检查高度范围
    altitude = track.altitude or 0
    if altitude < zone.min_altitude or altitude > zone.max_altitude:
        return None

    # 解析坐标
    coords = json.loads(zone.coordinates)
    is_inside = False
    distance_from_boundary = 0.0

    if zone.zone_type == "circle":
        center = coords["center"]
        radius = coords["radius"]
        is_inside, distance_from_boundary = is_point_in_circle(
            track.latitude, track.longitude,
            center["lat"], center["lng"],
            radius
        )
    elif zone.zone_type == "polygon":
        vertices = [(v["lat"], v["lng"]) for v in coords["vertices"]]
        is_inside, distance_from_boundary = is_point_in_polygon(
            track.latitude, track.longitude,
            vertices
        )

    if is_inside:
        return {
            "zone_id": zone.id,
            "track_id": track.track_id,
            "timestamp": track.timestamp,
            "latitude": track.latitude,
            "longitude": track.longitude,
            "altitude": altitude,
            "distance_from_boundary": distance_from_boundary,
            "intrusion_type": "breach" if distance_from_boundary < 0 else "inside",
        }

    return None


def detect_intrusions(
    db: Session,
    track_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> List[ZoneIntrusion]:
    """检测指定轨迹的禁飞区入侵"""
    # 获取激活的禁飞区
    zones = get_active_zones(db)

    # 获取修正后的轨迹数据
    query = db.query(FlightTrackCorrected).filter(FlightTrackCorrected.track_id == track_id)
    if start_time:
        query = query.filter(FlightTrackCorrected.timestamp >= start_time)
    if end_time:
        query = query.filter(FlightTrackCorrected.timestamp <= end_time)

    tracks = query.all()

    intrusions = []

    for track in tracks:
        for zone in zones:
            intrusion_info = check_intrusion(track, zone)
            if intrusion_info:
                # 检查是否已存在相同的入侵记录
                existing = db.query(ZoneIntrusion).filter(
                    ZoneIntrusion.zone_id == intrusion_info["zone_id"],
                    ZoneIntrusion.track_id == intrusion_info["track_id"],
                    ZoneIntrusion.timestamp == intrusion_info["timestamp"],
                ).first()

                if not existing:
                    # 创建入侵记录
                    intrusion = ZoneIntrusion(
                        zone_id=intrusion_info["zone_id"],
                        track_id=intrusion_info["track_id"],
                        timestamp=intrusion_info["timestamp"],
                        latitude=intrusion_info["latitude"],
                        longitude=intrusion_info["longitude"],
                        altitude=intrusion_info["altitude"],
                        intrusion_type=intrusion_info["intrusion_type"],
                        severity="high" if abs(intrusion_info["distance_from_boundary"]) > 100 else "medium",
                        distance_from_boundary=intrusion_info["distance_from_boundary"],
                        target_info=json.dumps({"confidence_score": track.confidence_score}),
                        notification_sent=0,
                    )
                    db.add(intrusion)
                    intrusions.append(intrusion)

    if intrusions:
        db.commit()

        # 发送邮件通知
        for intrusion in intrusions:
            zone = next(z for z in zones if z.id == intrusion.zone_id)
            if zone.notification_enabled:
                send_intrusion_notification(db, intrusion, zone)

    return intrusions


def send_intrusion_notification(
    db: Session,
    intrusion: ZoneIntrusion,
    zone: RestrictedZone,
) -> bool:
    """发送入侵预警邮件"""
    if not zone.notification_email or not settings.smtp_host:
        return False

    try:
        # 创建邮件
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[RFTIP 禁飞区入侵预警] {zone.zone_name}"
        msg["From"] = settings.smtp_user
        msg["To"] = zone.notification_email

        # 邮件内容
        html_content = f"""
        <html>
        <body>
            <h2>禁飞区入侵预警</h2>
            <p><strong>禁飞区名称：</strong>{zone.zone_name}</p>
            <p><strong>入侵时间：</strong>{intrusion.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>轨迹编号：</strong>{intrusion.track_id}</p>
            <p><strong>入侵位置：</strong>({intrusion.latitude:.6f}, {intrusion.longitude:.6f})</p>
            <p><strong>高度：</strong>{intrusion.altitude:.1f} 米</p>
            <p><strong>严重程度：</strong>{intrusion.severity}</p>
            <p><strong>距离边界：</strong>{abs(intrusion.distance_from_boundary):.1f} 米</p>
            <p>请及时处理！</p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_content, "html"))

        # 发送邮件
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)

        # 更新通知状态
        intrusion.notification_sent = 1
        db.commit()

        return True

    except Exception as e:
        print(f"发送邮件失败: {e}")
        return False


def get_intrusions(
    db: Session,
    zone_id: Optional[int] = None,
    track_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,
) -> List[ZoneIntrusion]:
    """查询入侵记录"""
    query = db.query(ZoneIntrusion)

    if zone_id is not None:
        query = query.filter(ZoneIntrusion.zone_id == zone_id)
    if track_id is not None:
        query = query.filter(ZoneIntrusion.track_id == track_id)
    if start_time is not None:
        query = query.filter(ZoneIntrusion.timestamp >= start_time)
    if end_time is not None:
        query = query.filter(ZoneIntrusion.timestamp <= end_time)

    return query.order_by(ZoneIntrusion.timestamp.desc()).limit(limit).all()
