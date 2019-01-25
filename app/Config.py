######################################
####### GENERAL CONFIGURATION ########
######################################

# True if we want to use the SUMO GUI
sumoUseGUI = False  # False

# which seed to be used in the random functions, for repeatability
random_seed = 1

epos_jar_path = "/Users/gerostat/Documents/research/EPOS CROWDNAV/release-0.0.1/epos-tutorial.jar"
######################################

######################################
#### CONFIGURATION OF SIMULATION #####
######################################

# The network config (links to the net) we use for our simulation
sumoConfig = "./app/map/eichstaedt.sumo.cfg"

# The network net we use for our simulation
sumoNet = "./app/map/eichstaedt.net.xml"

# The total number of cars we use in our simulation
totalCarCounter = 600

#
simulation_horizon = 299

######################################
##### CONFIGURATION OF PLANNING ######
######################################

#
start_with_epos_optimization = False

#
planning_period = 150

#
planning_steps = 3

#
planning_step_horizon = 100

# double from [0, 1], unfairness + selfishness <= 1, unfairness
alpha = 0

# double from [0, 1], unfairness + selfishness <= 1, selfishness or local objective
beta = 0
# alpha*unfairness + beta*local_cost + (1-alpha-beta)*global_costs

# Suggested values : "XCORR", VAR", "RSS", "RMSE"
globalCostFunction="VAR"

######################################
#### CONFIGURATION OF ADAPTATION #####
######################################

adaptation_period = 150