from pymavlink import mavutil
from pprint import pprint
from pymongo import MongoClient

def parse_telemetry(filepath, session_id, store_to_mongo=True):
    try:
        mav = mavutil.mavlink_connection(filepath, dialect="ardupilotmega", robust_parsing=True)
        all_msgs = []
        parsed_data = {}  # {msg_type: [list of dicts]}

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

            msg_dict['msg_type'] = msg_type
            msg_dict['session_id'] = session_id
            all_msgs.append(msg_dict)
            # Add to dict-of-lists for fast lookup by type
            if msg_type not in parsed_data:
                parsed_data[msg_type] = []
            parsed_data[msg_type].append(msg_dict)

        # Print preview (optional, remove if you like)
        if all_msgs:
            print("First record:")
            pprint(all_msgs[0])
            print("-" * 40)
            print("Keys in first 5 records:")
            for i, msg in enumerate(all_msgs[:5]):
                print(f"Message {i}: {list(msg.keys())}")
        else:
            print("No messages found.")

        # Store to MongoDB
        if store_to_mongo and all_msgs:
            client = MongoClient("mongodb://localhost:27017/")
            db = client['telemetry_db']
            db['telemetry_all'].insert_many(all_msgs)
            print(f"Inserted {len(all_msgs)} messages to MongoDB in 'telemetry_all' collection.")

        return parsed_data
    except Exception as e:
        return {"error": str(e)}
