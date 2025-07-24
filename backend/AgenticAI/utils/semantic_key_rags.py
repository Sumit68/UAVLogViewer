from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

key_descriptions = {
    "PARM": "Parameter values and configuration for the flight.",
    "ATT": "Attitude data: roll, pitch, yaw angles of the UAV.",
    "RATE": "Angular rate data for roll, pitch, and yaw.",
    "PIDR": "PID controller data for roll axis.",
    "PIDP": "PID controller data for pitch axis.",
    "PIDY": "PID controller data for yaw axis.",
    "PIDA": "PID controller data for altitude.",
    "FMTU": "Format unit, data field structure information.",
    "FTN": "Flight tuning data.",
    "IMU": "Inertial Measurement Unit sensor data: acceleration, gyroscope.",
    "ISBH": "Barometer sensor health information.",
    "ISBD": "Barometer sensor details.",
    "POWR": "Power module readings: voltages, currents.",
    "BAT": "Battery information: voltage, current, remaining power.",
    "MAG": "Magnetometer readings: compass data.",
    "ERR": "Logged errors and warnings during the flight.",
    "BARO": "Barometric altitude and pressure readings.",
    "CTUN": "Control tuning and setpoints for the flight controller.",
    "FTN1": "Flight tuning data group 1.",
    "FTN2": "Flight tuning data group 2.",
    "MOTB": "Motor outputs and balancing information.",
    "RCIN": "Radio control input signals.",
    "RCOU": "Radio control output signals.",
    "RCO2": "Second set of radio control output signals.",
    "PSCN": "Position controller navigation data.",
    "PSCE": "Position controller errors.",
    "PSCD": "Position controller debug data.",
    "VIBE": "Vibration data from onboard IMU sensors.",
    "CTRL": "Controller information: control mode, PID states.",
    "UNIT": "System unit settings.",
    "MULT": "Multiplexed data, multiple sources.",
    "MSG": "System messages, notifications, logs.",
    "VER": "Firmware and software version information.",
    "CMD": "Commands sent to the UAV.",
    "MODE": "Flight mode changes and history.",
    "FILE": "Log file events.",
    "STAK": "Stack usage and memory information.",
    "RCI2": "Second set of radio control input signals.",
    "HEAT": "Temperature and heating sensor data.",
    "MAV": "MAVLink communication events.",
    "DSF": "Dual sensor fusion data.",
    "DU32": "Data unit 32-bit values.",
    "XKF4": "Extended Kalman Filter (EKF4) status and outputs.",
    "XKF1": "Extended Kalman Filter group 1 outputs.",
    "XKF2": "Extended Kalman Filter group 2 outputs.",
    "XKF3": "Extended Kalman Filter group 3 outputs.",
    "XKF5": "Extended Kalman Filter group 5 outputs.",
    "XKFS": "EKF status summary.",
    "XKQ": "EKF quaternion outputs.",
    "XKV1": "EKF vector outputs group 1.",
    "XKV2": "EKF vector outputs group 2.",
    "XKT": "EKF timing information.",
    "IOMC": "IO MCU communication and status.",
    "MAVC": "MAVLink communication channel status.",
    "TSYN": "Time synchronization events.",
    "PM": "Power management status.",
    "RAD": "Radio signal quality and telemetry.",
    "PIDN": "PID controller data for navigation.",
    "PIDE": "PID controller data for elevator.",
    "AUXF": "Auxiliary functions status.",
    "GPS": "GPS data: position, speed, satellites, accuracy.",
    "GPA": "GPS accuracy and statistics.",
    "XKFM": "EKF miscellaneous outputs.",
    "AHR2": "Attitude and Heading Reference System 2 data.",
    "POS": "Position data: latitude, longitude, altitude."
}

def build_key_vectorstore():
    keys = list(key_descriptions.keys())
    descriptions = [key_descriptions[k] for k in keys]
    metadatas = [{"key": k} for k in keys]
    return FAISS.from_texts(descriptions, OpenAIEmbeddings(), metadatas=metadatas)

VECTORSTORE = build_key_vectorstore()

def identify_relevant_keys(query: str, top_k=1):
    docs = VECTORSTORE.similarity_search(query, k=top_k)
    return [doc.metadata["key"] for doc in docs]
