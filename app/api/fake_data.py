from app.api import api
from app import current_app
import json
from faker import Faker


# Generates test data for timeline

# TODO: Add hyperlinks to each analyzer's documentation when that's implemented
@api.route('/test-timeline-json', methods=['GET'])
def get_test_timeline_json():
    fake = Faker()
    data = []
    count = 1
    for i in range(5*100):
        current_app.logger.info(f'On folder: {count}')
        new_obj = {"text": str(count) + "..." + str(count + 999), "children": []}
        for j in range(1000):
            new_obj["children"].append({
                "text": "child:" + str(count)
            })
            count += 1
        data.append(new_obj)

    return data