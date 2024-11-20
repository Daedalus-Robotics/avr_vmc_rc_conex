from threading import Thread
from time import sleep

import rclpy
from rclpy import qos
from rclpy.node import Node
from std_srvs.srv import SetBool
from px4_msgs.msg import ManualControlSetpoint


class RCConexNode(Node):
    def __init__(self) -> None:
        super().__init__('rc_conex')

        self.trigger_client = self.create_client(
                SetBool,
                '/conex/set_dropper'
        )
        self.subscription = self.create_subscription(
                ManualControlSetpoint,
                '/fmu/out/manual_control_setpoint',
                self.rc_callback,
                qos.qos_profile_sensor_data
        )

        self.last_state = False

        self.get_logger().info('Waiting for set_dropper service...')
        self.trigger_client.wait_for_service()

        self.get_logger().info('Started')

        self.subscription

    def rc_callback(self, message: ManualControlSetpoint) -> None:
        state = message.aux1 > 0.1

        if state != self.last_state:
            request = SetBool.Request()
            request.data = state
            self.trigger_client.call_async(request)

        self.last_state = state


def main() -> None:
    rclpy.init()
    node = RCConexNode()
    executor = rclpy.executors.MultiThreadedExecutor()
    rclpy.spin(node, executor)


if __name__ == '__main__':
    main()
