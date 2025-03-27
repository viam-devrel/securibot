# Module securibot 

This module provides support for the [Securibot codelab](https://codelabs.viam.com) to automate a motion activated door based on a face recognition model.

## Model devrel:securibot:doorbot

The control logic service for reading detections from the face recognition vision service and moving the dependent servo for door access.

### Configuration
The following attribute template can be used to configure this model:

```json
{
    "camera_name": <string>,
    "servo_name": <string>,
    "vision_name": <string>
}
```

#### Attributes

The following attributes are available for this model:

| Name          | Type   | Inclusion | Description                |
|---------------|--------|-----------|----------------------------|
| `camera_name` | string  | Required  | Name of the camera component to pass to the vision service for detections |
| `servo_name` | string | Required  | Name of the servo component to use for actuation |
| `vision_name` | string | Required  | Name of the vision service to use for detections |

#### Example Configuration

```json
{
    "camera_name": "camera-1",
    "servo_name": "servo-1",
    "vision_name": "vision-1"
}
```

### DoCommand

This module implements the following commands to be used by the `DoCommand` method in the Control tab of the Viam app or one of the language SDKs.

**start**

Start the control loop for reading the webcam data, comparing it to known faces, and triggering the servo motor.

```json
{
    "start": []
}
```

**stop**

Stop the control loop.

```json
{
    "stop": []
}
```
