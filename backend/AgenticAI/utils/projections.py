# AgenticAI/utils/projections.py

# Projection fields for relevant ArduPilot msg_types
PROJECTION_FIELDS = {
    "GPS": {
        "TimeUS": 1, "NSats": 1, "HDop": 1, "Lat": 1,
        "Lng": 1, "Alt": 1, "Spd": 1, "GCrs": 1, "_id": 0
    },
    "BAT": {
        "TimeUS": 1, "Volt": 1, "Curr": 1, "CurrTot": 1,
        "EnrgTot": 1, "_id": 0
    },
    "POWR": {
        "TimeUS": 1, "Vcc": 1, "Servo": 1, "_id": 0
    },
    "ERR": {
        "TimeUS": 1, "Subsys": 1, "ECode": 1, "_id": 0
    },
    "IMU": {
        "TimeUS": 1, "GyrX": 1, "GyrY": 1, "GyrZ": 1,
        "AccX": 1, "AccY": 1, "AccZ": 1, "_id": 0
    },
    "VIBE": {
        "TimeUS": 1, "VibeX": 1, "VibeY": 1, "VibeZ": 1,
        "Clip0": 1, "Clip1": 1, "Clip2": 1, "_id": 0
    },
    "MAG": {
        "TimeUS": 1, "MagX": 1, "MagY": 1, "MagZ": 1, "_id": 0
    },
    "RCIN": {
        "TimeUS": 1, "C1": 1, "C2": 1, "C3": 1, "C4": 1, "_id": 0
    },
    "RCOU": {
        "TimeUS": 1, "C1": 1, "C2": 1, "C3": 1, "C4": 1, "_id": 0
    },
    "MODE": {
        "TimeUS": 1, "Mode": 1, "ModeNum": 1, "_id": 0
    },
    "MSG": {
        "TimeUS": 1, "Message": 1, "_id": 0
    },
    "CTUN": {
        "TimeUS": 1, "ThO": 1, "Alt": 1, "BAlt": 1, "DAlt": 1, "_id": 0
    },
    "HEAT": {
        "TimeUS": 1, "T": 1, "TD": 1, "_id": 0
    },
    "BARO": {
        "TimeUS": 1, "Alt": 1, "Press": 1, "_id": 0
    },
    "ARSP": {
        "TimeUS": 1, "AS": 1, "_id": 0
    },
    "EKF1": {
        "TimeUS": 1, "HA": 1, "VN": 1, "VE": 1, "VD": 1, "_id": 0
    }
}

def get_projection(key: str):
    """Return projection for a given msg_type (key), or a fallback."""
    return PROJECTION_FIELDS.get(key, {"TimeUS": 1, "_id": 0})
