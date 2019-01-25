import json
import traci
import traci.constants as tc
from app.network.Network import Network

from colorama import Fore

from app import Config
from app.entity.CarRegistry import CarRegistry
from app.logging import info
from app.routing.CustomRouter import CustomRouter
import time

from app.logging import CSVLogger

import app.Util as Util
from app.adaptation.Adaptation import Adaptation
from app.adaptation import Knowledge

current_milli_time = lambda: int(round(time.time() * 1000))


class Simulation(object):
    """ here we run the simulation in """

    # the current tick of the simulation
    tick = 0

    # last tick time
    lastTick = current_milli_time()

    @classmethod
    def applyFileConfig(cls):
        """ reads configs from a json and applies it at realtime to the simulation """
        try:
            config = json.load(open('./knobs.json'))
            CustomRouter.explorationPercentage = config['explorationPercentage']
            CustomRouter.averageEdgeDurationFactor = config['averageEdgeDurationFactor']
            CustomRouter.maxSpeedAndLengthFactor = config['maxSpeedAndLengthFactor']
            CustomRouter.freshnessUpdateFactor = config['freshnessUpdateFactor']
            CustomRouter.freshnessCutOffValue = config['freshnessCutOffValue']
            CustomRouter.reRouteEveryTicks = config['reRouteEveryTicks']
        except:
            pass

    @classmethod
    def start(cls):

        Knowledge.planning_period = Config.planning_period
        Knowledge.planning_step_horizon = Config.planning_step_horizon
        Knowledge.planning_steps = Config.planning_steps
        Knowledge.alpha = Config.alpha
        Knowledge.beta = Config.beta
        Knowledge.globalCostFunction = Config.globalCostFunction

        Util.remove_overhead_and_streets_files()

        CSVLogger.logEvent("streets", [edge.id for edge in Network.routingEdges])

        Util.prepare_epos_input_data_folders()

        """ start the simulation """
        info("# Start adding initial cars to the simulation", Fore.MAGENTA)
        # apply the configuration from the json file
        cls.applyFileConfig()
        CarRegistry.applyCarCounter()

        if Config.start_with_epos_optimization:
            CarRegistry.replaceAll("conf/epos.properties", "numAgents=", "numAgents=" + str(Config.totalCarCounter))
            CarRegistry.replaceAll("conf/epos.properties", "planDim=", "planDim=" + str(Network.edgesCount() * Knowledge.planning_steps))
            CarRegistry.replaceAll("conf/epos.properties", "alpha=", "alpha=" + str(Knowledge.alpha))
            CarRegistry.replaceAll("conf/epos.properties", "beta=", "beta=" + str(Knowledge.beta))
            CarRegistry.replaceAll("conf/epos.properties", "globalCostFunction=", "globalCostFunction=" + str(Knowledge.globalCostFunction))

            cars_to_indexes = {}
            for i in range(Config.totalCarCounter):
                cars_to_indexes["car-" + str(i)] = i
            CarRegistry.run_epos_apply_results(True, cars_to_indexes)

        cls.loop()

    @classmethod
    # @profile
    def loop(cls):
        """ loops the simulation """

        # start listening to all cars that arrived at their target
        traci.simulation.subscribe((tc.VAR_ARRIVED_VEHICLES_IDS,))
        while 1:

            if len(CarRegistry.cars) == 0:
                print("all cars reached their destinations")
                return

            # Do one simulation step
            cls.tick += 1
            traci.simulationStep()

            # Check for removed cars and re-add them into the system
            for removedCarId in traci.simulation.getSubscriptionResults()[122]:
                CarRegistry.findById(removedCarId).setArrived(cls.tick)

            CSVLogger.logEvent("streets", [cls.tick] + [traci.edge.getLastStepVehicleNumber(edge.id)*CarRegistry.vehicle_length / edge.length for edge in Network.routingEdges])

            # print status update if we are not running in parallel mode
            if (cls.tick % 100) == 0:
                print("Simulation -> Step:" + str(cls.tick) + " # Driving cars: " + str(
                    traci.vehicle.getIDCount()) + "/" + str(
                    CarRegistry.totalCarCounter) + " # avgTripDuration: " + str(
                    CarRegistry.totalTripAverage) + "(" + str(
                    CarRegistry.totalTrips) + ")" + " # avgTripOverhead: " + str(
                    CarRegistry.totalTripOverheadAverage))

            if Config.simulation_horizon == cls.tick:
                print("Simulation horizon reached!")
                return

            if (cls.tick % Knowledge.planning_period) == 0:
                CarRegistry.do_epos_planning(cls.tick)

            if (cls.tick % Config.adaptation_period) == 0:
                Adaptation.sense_and_adapt(cls.tick)