import globals

# def filter_illuminocity_events(raw_ds):
#     pass

def prepare_illuminocity_data(dataset):
    all_data = []
    for event in dataset:
        if event['eventType'] == 'IOT_TELEMETRY' and 'illuminance' in event['iotTelemetry']:
            illuminance_data = event['iotTelemetry']['illuminance']
            xPos = event['iotTelemetry']['detectedPosition']['xPos']
            yPos = event['iotTelemetry']['detectedPosition']['yPos']
            illum_value = illuminance_data.get('value', 0)  # Default to 0 if 'value' is not present
            all_data.append({'x': xPos, 'y': yPos, 'illum': illum_value})
    return all_data
