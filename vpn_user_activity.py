import vici
import json
from flask import Flask, Response
from prometheus_client import generate_latest, Gauge


app = Flask(__name__)

tags = {'name', 'bytes-in', 'bytes-out'}
vpn_traffic = Gauge('vpn_traffic', 'VPN traffic statistics', ['client_name', 'direction'])


# Endpoint to expose metrics on demand
@app.route('/metrics')
def expose_metrics():
    update_metrics()  # Update the gauge before exposing metrics
    return Response(generate_latest(), mimetype='text/plain')


def update_metrics():
    vpn_user_activity = get_vpn_user_activity()
    for stats in vpn_user_activity:
        user = stats.get('name').decode('utf-8')
        bytes_in = int(stats.get('bytes-in'))
        bytes_out = int(stats.get('bytes-out'))
        vpn_traffic.labels(client_name = user, direction = 'in').set(bytes_in)
        vpn_traffic.labels(client_name = user, direction = 'out').set(bytes_out)


def get_vpn_user_activity():
    vpn_user_activity = []
    vici_session = vici.Session()
    for sas in vici_session.list_sas():
        stats = {key: None for key in tags}
        for tag in stats:
            stats[tag] = find_value_by_key(sas, tag)
        vpn_user_activity.append(stats)
    return vpn_user_activity



def find_value_by_key(data, target_key):
    for key, value in data.items():
        if key == target_key:
            return value
        elif isinstance(value, dict):
            # Recursive call for nested dictionaries
            result = find_value_by_key(value, target_key)
            if result is not None:
                return result
        elif isinstance(value, list):
            # Recursive call for nested lists
            for item in value:
                if isinstance(item, dict):
                    result = find_value_by_key(item, target_key)
                    if result is not None:
                        return result
    return None


def main():
    #app.run(host='0.0.0.0', port=9101)
    app.run()


if __name__ == "__main__":
    main()
