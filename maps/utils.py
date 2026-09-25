"""Distance helpers used instead of PostGIS, since we store lat/lng as plain
DecimalFields (see settings comment on why: SQLite has no geo extension by
default and PostGIS would be overkill for this project)."""
import math

EARTH_RADIUS_MILES = 3958.8
EARTH_RADIUS_KM = 6371.0


def haversine_distance(lat1, lng1, lat2, lng2, unit="miles"):
    """Great-circle distance between two lat/lng points.

    US-8/US-9: used to filter map jobs by distance from the seeker's current
    location and to support a preferred commute radius.

    All of lat1/lng1/lat2/lng2 may be ``float`` or ``Decimal``; any of them
    being ``None`` returns ``None`` (caller should treat that as "unknown
    distance", not zero).
    """
    if None in (lat1, lng1, lat2, lng2):
        return None

    lat1, lng1, lat2, lng2 = map(lambda v: math.radians(float(v)), (lat1, lng1, lat2, lng2))
    dlat = lat2 - lat1
    dlng = lng2 - lng1

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    radius = EARTH_RADIUS_MILES if unit == "miles" else EARTH_RADIUS_KM
    return radius * c


def filter_by_radius(points, center_lat, center_lng, radius, unit="miles"):
    """Filter an iterable of objects with ``.latitude``/``.longitude`` to
    those within ``radius`` of (center_lat, center_lng).

    TODO(US-8/US-9): Wire this into the map JSON endpoint once the frontend
    sends the seeker's current location (browser geolocation) and chosen
    commute radius as query params.
    """
    if center_lat is None or center_lng is None or radius is None:
        return list(points)

    result = []
    for point in points:
        distance = haversine_distance(center_lat, center_lng, point.latitude, point.longitude, unit=unit)
        if distance is not None and distance <= radius:
            result.append(point)
    return result
