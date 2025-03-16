import os
import commands2
import wpilib
import choreo

DEFAULT_TRAJECTORY = 'outwayred'

class FollowTrajectory(commands2.Command):
    def __init__(self, drivetrain, intake, traj, is_red_alliance) -> None:
        """
        Initializes the AutonomousCommand.

        :param drivetrain: The drivetrain subsystem used by this command.
        :param traj: The trajectory file to follow.
        :param is_red_alliance: Boolean indicating if the robot is on the red alliance.
        """
        super().__init__()
        self.drivetrain = drivetrain
        self.intake = intake
        self.trajectory = choreo.load_swerve_trajectory(traj)
        self.timer = wpilib.Timer()
        self.is_red_alliance = is_red_alliance
        self.laststamp = 0
        self.event_markers = []
        self.triggered_events = set()

        self.addRequirements(self.drivetrain)  # Ensure the drivetrain is a requirement for this command
        

    def initialize(self) -> None:
        """
        This autonomous runs the autonomous command selected by your RobotContainer class.
        """
        if self.trajectory:
            # Get the initial pose of the trajectory
            initial_pose = self.trajectory.get_initial_pose(self.is_red_alliance)

            if initial_pose:
                # Reset odometry to the start of the trajectory
                self.drivetrain.reset_pose(initial_pose)

            # Load event markers from the trajectory
            self.event_markers = self.trajectory.events

        # Reset and start the timer when the autonomous period begins
        self.finished = False
        self.timer.restart()

    def execute(self) -> None:
        """
        This function is called periodically during autonomous.
        """
        if self.trajectory:
            # Sample the trajectory at the current time into the autonomous period
            sample = self.trajectory.sample_at(self.timer.get(), self.is_red_alliance)

            if sample:
                if sample.timestamp != self.laststamp:
                    # Command the drivetrain to follow the sampled trajectory
                    self.drivetrain.follow_trajectory(sample)
                    self.laststamp = sample.timestamp

                    # Check for event markers and trigger actions
                    for marker in self.event_markers:
                        if marker.timestamp <= self.timer.get() < marker.timestamp + 0.2:
                            if marker.event not in self.triggered_events:
                                self.triggerEvent(marker.event)
                                self.triggered_events.add(marker.event)

                else:
                    self.finished = True

    def triggerEvent(self, event) -> None:
        """
        Trigger the action associated with the event.
        """
        # Implement the actions to be triggered by the event
        if event == "CoralPlace":
            # Perform some action
            self.intake.setMotor(1)
        elif event == "CoralIntake":
            # Perform another action
            self.intake.setMotor(0.3)
        elif event == "ResetHeading":
            self.drivetrain.seed_field_centric()

    def isFinished(self) -> bool:
        """
        Returns true when the command should end.
        """
        if self.finished:
            self.drivetrain.stop()
            return True
        return False

def createChooser() -> wpilib.SendableChooser:
    traj_dir = f"{wpilib.getOperatingDirectory()}/deploy/choreo"
    traj_files = []
    for f in os.listdir (traj_dir):
        if f.endswith('.traj'):
            traj_files.append (f)
    
    chooser = wpilib.SendableChooser()
    for traj_file in traj_files:
        chooser.addOption (traj_file.removesuffix ('.traj'),
                                traj_file.removesuffix ('.traj'))        
    chooser.setDefaultOption (DEFAULT_TRAJECTORY, DEFAULT_TRAJECTORY)
    return chooser
