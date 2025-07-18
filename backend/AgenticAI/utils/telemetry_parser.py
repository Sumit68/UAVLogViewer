from pymavlink import mavutil
def parse_telemetry(filepath):
    try:
        mav = mavutil.mavlink_connection(filepath, dialect="ardupilotmega", robust_parsing=True)
        parsed_data = {}

        while True:
            msg = mav.recv_match(blocking=True)
            if msg is None:
                break

            msg_type = msg.get_type()
            if msg_type == "FMT":
                continue

            try:
                msg_dict = msg.to_dict()
            except Exception:
                continue

            for key, value in msg_dict.items():
                if isinstance(value, bytes):
                    msg_dict[key] = value.decode(errors="ignore")
                elif hasattr(value, "tolist"):
                    msg_dict[key] = value.tolist()

            if msg_type not in parsed_data:
                parsed_data[msg_type] = []

            parsed_data[msg_type].append(msg_dict)
        return parsed_data

    except Exception as e:
        return {"error": str(e)}
