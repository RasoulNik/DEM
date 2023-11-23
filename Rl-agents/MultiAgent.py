import numpy as np
from keras import models
from tensorflow.keras.optimizers import Adam
from random import randrange
from collections import deque
import torch
from buffer import ReplayBuffer
import glob
from utils import save, collect_random
import random





class Multi_Agent:
    def __init__(self, agent_class, env, config, config_name, agent_id):
        self.config = config
        self.config_name = config_name
        self.env = env
        self.agent_id= agent_id
        self.len_episode = int(self.config.get('DRL', 'Max_Episode'))
        self.agents = agent_class(self.env, config, self.agent_id)
        self.drl_class = self.config.get('DRL', '_class_ML')

    def run(self):
        score_log = []
        diffpro_log = []
        battery_log = []
        list_r=[]
        done = False
        score = 0
        state = self.env.reset()
        state = np.reshape(state, [1, self.env.observation_space.shape[0]])
        steps = 0
        steps_ = 0
        eps = 1.
        d_eps = 1 - 0.01 #Minimal Epsilon
        if self.drl_class == 'DSAC':
            state = self.env.reset()
            '''
            np.random.seed(1)
            random.seed(1)
            torch.manual_seed(1)
            self.env.seed(1)
            self.env.action_space.seed(1)
            '''
            buffer = ReplayBuffer(buffer_size=100_000, batch_size=256,
                              device=torch.device("cuda:0" if torch.cuda.is_available() else "cpu"))
            collect_random(env=self.env, dataset=buffer, num_samples=1000)
        





        while not done:
            # get action for the current state and go one step in environment
            
            if self.drl_class == 'DSAC':
                action = self.agents.get_action(state)
                steps += 1
                #action = randrange(2)

                next_state, reward, done, info = self.env.step(action)
                buffer.add(state, action, reward, next_state, done)
                self.agents.learn(steps, buffer.sample(), gamma=0.99)
                state = next_state
                score += reward
                list_r.append(reward)
                




            

            diffpro_log.append(info.get('dic_diffpro'))
            battery_log.append(info.get('dic_battery'))




            if done:

                self.agents.avg_reward_per_house.append(np.mean(list_r))
                print("step------------------------------", steps)
              

                self.agents.best_score = score
                #self.agents.best_score = np.mean(list_r)
                self.agents.best_diffpro = np.mean(diffpro_log)
                self.agents.best_battery = np.mean(battery_log)