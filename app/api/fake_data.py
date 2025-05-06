from app.api import api
from app import current_app
import json
from faker import Faker


# Generates test data for timeline

# TODO: Add hyperlinks to each analyser's documentation when that's implemented
@api.route('/test-timeline-json', methods=['GET'])
def get_test_timeline_json():
    fake = Faker()
    data = []
    count = 1
    for h in range(5):
        timeline = []
        for i in range(1):
            new_obj = {"text": str(count) + "...", "children": []}
            for j in range(10):
                new_obj["children"].append({
                    "text": "child:" + str(count)
                })
                count += 1
            timeline.append(new_obj)
        data.append(timeline)

    return data