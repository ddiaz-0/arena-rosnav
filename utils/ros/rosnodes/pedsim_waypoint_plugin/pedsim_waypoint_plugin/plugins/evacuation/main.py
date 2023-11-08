from pedsim_waypoint_plugin.pedsim_waypoint_generator import OutputData, PedsimWaypointGenerator, InputData, WaypointPluginName, WaypointPlugin
import pedsim_msgs.msg
import Integrators
from diff_equation import Diff_Equ
from Room import Room
import numpy as np


@PedsimWaypointGenerator.register(WaypointPluginName.EVACUATION)
class Plugin_Evacuation(WaypointPlugin):
    def __init__(self):
        ...

    def callback(self, data) -> OutputData:
        '''
        "num_steps" is the duration the simulation will run (recommended:1000)

       "method" is the method of integration. You should use leap_frog even though it will often explode
        since more relaible methods of integration like ode45 and monto carlo take a lot a computational power.
        '''
        tau = 1                                         # time-step (s), TODO: figure out right value
        num_steps = 2                                   # the number of force-calculation steps the simulation should go through (each callback should be 1 step?)
        room_size = 500                                 # size of square room (m), TODO: has to be deleted or changed
        room = Room("square", room_size)                # kind of room the simulation runs in, TODO: has to be deleted or changed
        method = getattr(Integrators, "leap_frog")      # method used for integration -> leap-frog was the GoTo solution in the original project
        N = len(data.agents)                            # quantity of pedestrians aka the number of agents that are currently in the simulation
        
        v = np.zeros((2, N, num_steps))                 # Three dimensional array of velocity, not used in leap frog strangely
        y = np.zeros((2, N, num_steps))                 # Three dimensional array of place: x = coordinates, y = Agent, z=Time, TODO: figure out right value
        for i in range(N):
            x = data.agents[i].pose.position.x
            y = data.agents[i].pose.position.y
            pos = [x, y] 
            y[:, i, 0] = pos     

        radii = 0.4 * np.ones(N)                        # radii of pedestrians (m) -> was "0.4 * (np.ones(self.N)*variation).squeeze()" before
        m = 80 * np.ones(N)                             # mass of pedestrians (kg) -> was "80 * (np.ones(self.N)*variation).squeeze()" before

        #create differential equation object
        diff_equ = Diff_Equ(N, room_size, tau, room, radii, m)  # initialize Differential equation

        # calls the method of integration with the starting positions, diffequatial equation, number of steps, and delta t = tau
        # v is not used in leap frog (why?)
        y, agents_escaped, forces = method(y[:, :, 0], v[:, :, 0], diff_equ.f, num_steps, tau, room)
           
        feedbacks = []

        for agent, force in zip(data.agents,forces):
            #copied from Nhat
            feedback = pedsim_msgs.msg.AgentFeedback()
            feedback.id = agent.id
            feedback.force.x = force[0] #TODO
            feedback.force.y = force[1] #TODO
            feedbacks.append(feedback)

        return feedbacks
        

        #return [calculate_forces(agent) for agent in data.agents]
