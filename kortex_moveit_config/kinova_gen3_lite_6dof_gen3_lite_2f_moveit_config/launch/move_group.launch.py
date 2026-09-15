import os

from moveit_configs_utils import MoveItConfigsBuilder

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from moveit_configs_utils.launch_utils import DeclareBooleanLaunchArg, add_debuggable_node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():

    ld = LaunchDescription()

    ld.add_action(DeclareLaunchArgument("prefix", default_value=""))
    ld.add_action(DeclareLaunchArgument("origin_xyz", default_value="0 0 0"))
    ld.add_action(DeclareLaunchArgument("origin_rpy", default_value="0 0 0"))

    xacro_args = {
        "robot_ip": "xxx.yyy.zzz.www",
        "name": "gen3_lite",
        "arm": "gen3_lite",
        "dof": "6",
        "vision": "False",
        "prefix": LaunchConfiguration("prefix"),
        "origin_xyz": LaunchConfiguration("origin_xyz"),
        "origin_rpy": LaunchConfiguration("origin_rpy"),
        "sim_gazebo": "False",
        "sim_ignition": "True",
        "simulation_controllers": "/workspaces/vscode_moveit_humble/src/ros2_kortex/kortex_description/arms/gen3_lite/6dof/config/ros2_controllers.yaml",
        "gripper": "gen3_lite_2f",
    }
    moveit_config = (
        MoveItConfigsBuilder("gen3_lite", package_name="kinova_gen3_lite_6dof_gen3_lite_2f_moveit_config")
        .robot_description(mappings=xacro_args)
        .to_moveit_configs()
    )
    

    ld.add_action(DeclareBooleanLaunchArg("debug", default_value=False))
    ld.add_action(DeclareBooleanLaunchArg("use_sim_time", default_value=False))
    ld.add_action(
        DeclareBooleanLaunchArg("allow_trajectory_execution", default_value=True)
    )
    ld.add_action(
        DeclareBooleanLaunchArg("publish_monitored_planning_scene", default_value=True)
    )
    # load non-default MoveGroup capabilities (space separated)
    ld.add_action(DeclareLaunchArgument("capabilities", default_value=""))
    # inhibit these default MoveGroup capabilities (space separated)
    ld.add_action(DeclareLaunchArgument("disable_capabilities", default_value=""))

    # do not copy dynamics information from /joint_states to internal robot monitoring
    # default to false, because almost nothing in move_group relies on this information
    ld.add_action(DeclareBooleanLaunchArg("monitor_dynamics", default_value=False))


    should_publish = LaunchConfiguration("publish_monitored_planning_scene")

    move_group_configuration = {
        "publish_robot_description_semantic": True,
        "allow_trajectory_execution": LaunchConfiguration("allow_trajectory_execution"),
        # Note: Wrapping the following values is necessary so that the parameter value can be the empty string
        "capabilities": ParameterValue(
            LaunchConfiguration("capabilities"), value_type=str
        ),
        "disable_capabilities": ParameterValue(
            LaunchConfiguration("disable_capabilities"), value_type=str
        ),
        # Publish the planning scene of the physical robot so that rviz plugin can know actual robot
        "publish_planning_scene": should_publish,
        "publish_geometry_updates": should_publish,
        "publish_state_updates": should_publish,
        "publish_transforms_updates": should_publish,
        "monitor_dynamics": False,
        "use_sim_time": LaunchConfiguration("use_sim_time"),
    }

    move_group_params = [
        moveit_config.to_dict(),
        move_group_configuration,
    ]

    add_debuggable_node(
        ld,
        package="moveit_ros_move_group",
        executable="move_group",
        commands_file=str(moveit_config.package_path / "launch" / "gdb_settings.gdb"),
        output="screen",
        parameters=move_group_params,
        extra_debug_args=["--debug"],
        # Set the display variable, in case OpenGL code is used internally
        additional_env={"DISPLAY": os.environ["DISPLAY"]},
    )

    return ld
