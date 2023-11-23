#CUDA_VISIBLE_DEVICES=0 python3 main.py --config Config_house/Progressus.properties
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import configparser
import argparse
import numpy as np
import random
import gym
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from house import registration
#from Agent import DDPG, DQN, DDQN
from Agent import DQN, DDQN, A2C, DSAC, DDPG, Random_Battery, Random
from MultiAgent import Multi_Agent
import time
import pylab
import pickle




def main():
    start = time.time()


    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='Config_Progressus/config.properties')
    args = parser.parse_args()
    config_name = args.config.replace('/', ',').replace('.', ',').split(',')[1]

    # Read configuration file
    config = configparser.RawConfigParser(defaults=None, strict=False)
    config.read(args.config)

    global_seed = int(config.get('Simulation', 'global_seed'))
    n_house = int(config.get('Simulation', 'n_house'))
    n_decisions_per_episode = int(config.get('DRL', 'Max_Episode'))
    n_fed_episodes = int(config.get('DRL', 'n_episodes'))
    registration(n_decisions_per_episode)

    ENV_dic = {}
    AGENTS_dic = {}
    score_log = {}
    Reward_list=[]
    Reward_list_agent0 = []
    diffpro_list=[]
    battery_list = []
    episodes_list=[]
    drl_class_NAME=''
    if n_house > 1:
        federation_mode = True
    else:
        federation_mode = False
    Reward_list_fed = []
    diffpro_list_fed = []
    battery_list_fed = []
    # Instantiation of Gym environments for every House
   
    if config.get('DRL', '_class_ML') == 'DSAC':
        drl_class = DSAC
        drl_class_NAME = 'DSAC'
 




    for i in range(n_house):
        key = 'env' + str(i + 1)
        if key not in ENV_dic.keys():
            ENV_dic[key] = gym.make('Progressus-v0',
                                    global_seed=global_seed,
                                    configfile=args.config,
                                    agent_id=i,
                                    n_agents=n_house
                                    )
            AGENTS_dic[key] = Multi_Agent(drl_class, ENV_dic[key], config, config_name, i)

    # Train the Agents for n_episodes
    for j in range(int(config.get('DRL', 'n_episodes'))):
        # save the model

        print("Episode = ",j,"/", config.get('DRL', 'n_episodes'))

        # Multiprocessing
#        with ProcessPoolExecutor(10) as executor:
        for i in range(n_house):
            #p_process[i] = executor.submit(AGENTS_dic[('env' + str(i + 1))].run())
            AGENTS_dic[('env' + str(i + 1))].run()
            

    end = time.time()
    simulation_time = end-start

    print("#####################################################################################")
    print("####################### Simulation done in : ", simulation_time)
    print("#####################################################################################")

if __name__ == "__main__":
    main()
