import asyncio
from threading import Event
from typing import ClassVar, Mapping, Optional, Sequence, cast

from typing_extensions import Self
from viam.components.servo import Servo
from viam.services.vision import VisionClient
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.services.generic import Generic
from viam.utils import ValueTypes, struct_to_dict


class Doorbot(Generic, EasyResource):
    # To enable debug-level logging, either run viam-server with the --debug option,
    # or configure your resource/machine to display debug logs.
    MODEL: ClassVar[Model] = Model(ModelFamily("devrel", "securibot"), "doorbot")

    auto_start = True
    task = None
    event = Event()

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """This method creates a new instance of this Generic service.
        The default implementation sets the name from the `config` parameter and then calls `reconfigure`.

        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The dependencies (both implicit and explicit)

        Returns:
            Self: The resource
        """
        return super().new(config, dependencies)

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        """This method allows you to validate the configuration object received from the machine,
        as well as to return any implicit dependencies based on that `config`.

        Args:
            config (ComponentConfig): The configuration for this resource

        Returns:
            Sequence[str]: A list of implicit dependencies
        """
        attrs = struct_to_dict(config.attributes)
        servo_name, vision_name, camera_name = (
            attrs.get("servo_name"),
            attrs.get("vision_name"),
            attrs.get("camera_name"),
        )
        if any(dep is None for dep in [servo_name, vision_name, camera_name]):
            raise Exception("servo_name and vision name are required to be configured.")

        return [str(servo_name), str(vision_name)]

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """This method allows you to dynamically update your service when it receives a new `config` object.

        Args:
            config (ComponentConfig): The new configuration
            dependencies (Mapping[ResourceName, ResourceBase]): Any dependencies (both implicit and explicit)
        """
        attrs = struct_to_dict(config.attributes)
        servo_name, vision_name, self.camera_name = (
            str(attrs.get("servo_name")),
            str(attrs.get("vision_name")),
            str(attrs.get("camera_name")),
        )
        self.access_list = list(attrs.get("access_list"))

        self.servo = cast(Servo, dependencies[Servo.get_resource_name(servo_name)])
        self.vision = cast(
            VisionClient, dependencies[VisionClient.get_resource_name(vision_name)]
        )

        if self.auto_start:
            self.start()

    async def on_loop(self):
        detections = []
        try:
            detections = await self.vision.get_detections_from_camera(self.camera_name)
        except Exception as err:
            self.logger.error(f"Error while getting detections: {err}")

        for d in detections:
            if d.class_name in self.access_list:
                self.logger.info(f"Access granted to {d.class_name}")
                await self.openDoor()
                break

        await asyncio.sleep(1)

    async def openDoor(self):
        close_pos = 10
        current_pos = await self.servo.get_position()
        open_pos = current_pos + 50
        await self.servo.move(open_pos)
        await asyncio.sleep(1)
        await self.servo.move(close_pos)

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Mapping[str, ValueTypes]:
        result = {key: False for key in command.keys()}
        for name, _args in command.items():
            if name == "start":
                self.start()
                result[name] = True
            if name == "stop":
                self.stop()
                result[name] = True
        return result

    def start(self):
        loop = asyncio.get_event_loop()
        self.task = loop.create_task(self.control_loop())
        self.event.clear()

    def stop(self):
        self.event.set()
        if self.task is not None:
            self.task.cancel()

    async def control_loop(self):
        while not self.event.is_set():
            await self.on_loop()
            await asyncio.sleep(0)

    def __del__(self):
        self.stop()

    async def close(self):
        self.stop()
