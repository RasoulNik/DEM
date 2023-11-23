import gym

from gym import spaces

from collections import OrderedDict

import configparser

import numpy as np

import tensorflow as tf

import tensorflow_probability as tfp

import math

import pandas

from scipy.stats import poisson

import pickle


def registration(max_episode):
    gym.envs.register(id='Progressus-v0',

                      entry_point='house:ProgressusEnv',

                      max_episode_steps=max_episode,

                      kwargs={

                          'global_seed': None,

                          'configfile': None,

                          'agent_id': None,

                          'n_agents': None

                      })


class ProgressusEnv(gym.Env):
    def __init__(self, global_seed=None, configfile=None, agent_id=None, n_agents=None):
        # Simulation Section
        self.global_seed = global_seed
        self.agent_id = agent_id
        self.n_agents = n_agents
        self.data_time = 0
        self.sell_price = .0
        self.action_space = spaces.Discrete(5)
        # self.action_space = spaces.Discrete(4)
        self.config = configparser.RawConfigParser(defaults=None, strict=False)
        self.config.read(configfile)
  
        # load data (csv)
        df = pandas.read_csv(self.config.get('Simulation', 'envTrain'), sep=",", header=0)
        df['Date and time (UTC)'] = pandas.to_datetime(df['Date and time (UTC)'])
        df['hour'] = df['Date and time (UTC)'].dt.hour
        data = df.iloc[self.agent_id::self.n_agents]
        self.data = data.values
        self.data_time = data['hour'].values
        # €29.66 per 100 kilowatt-hour
        # €0.0002966 per watt-hour
        self.sell_price = (.3 * (1 - np.exp(-((self.data_time - 14) ** 2) / 5))) * 1e-3
        if self.agent_id == 0:
            with open('Time.pkl', 'ab') as f:
                pickle.dump(self.data_time, f)
            with open('price.pkl', 'ab') as f:
                pickle.dump(self.sell_price, f)
        self.panelProdMax = max(self.data[:, 5]) 
        self.consumptionMax = max(self.data[:, 4])
        self.priceMax = max(abs(self.data[:, 3]))
        # print("max price", self.priceMax)
        self.data[:, 5] /= 1 # in kW. production
        self.data[:, 4] /= 1000  # in kW. consumption
        # self.data[:, 3] /= self.priceMax
        self.data[:, 3] /= 100  # in euros per kWh
        self.currentState_row = 0
        self.currentState_price = self.data[self.currentState_row, 3] # in euros per kWh
        self.currentState_consumption = self.data[self.currentState_row, 4] # in kw
        self.currentState_panelProd = self.data[self.currentState_row, 5]# in kw
        self.currentState_battery = 0.0
        self.diffProd = 0
        # Capacity of the battery
        self.batteryCapacity = 2 # kWh
        # CO2 price/emissions
        self.co2Price = 25.0 * 0.001  # price per ton of CO2 (mean price from the european market)
        self.co2Generator = 8 * 0.001  # kg of CO2 generated per kWh from the diesel generator
        self.co2Market = (
            0.3204  # kg of CO2 generated per kWh from the national power market (danish)
        )
        # Operational Rewards
        self.chargingReward = 0.0
        self.dischargingReward = 0.0
        # self.solarRewards = 0.0
        self.generatorReward = 0.0  # 0.314 à 0.528 $/kWh
        # Yields
        self.chargingYield = 1.0
        self.dischargingYield = 1.0
        self.state = None

              # please, keep the lase element obs space element devoted to track agents prb allocation
        OBS_SPACE_DIM = 3
        high = np.array((self.batteryCapacity,self.panelProdMax,self.consumptionMax/1000, 24), dtype=np.float32)
        low = np.array((0, 0, 0, 0), dtype=np.float32)
        # low = np.zeros((OBS_SPACE_DIM,), dtype=np.float32)
        # low = np.ones((OBS_SPACE_DIM,), dtype=np.float32)
        self.observation_space = spaces.Box(low, high, dtype=np.float32)
        # self.reset()
        # self.seed()

    def step(self, action):
        #  map action to the corresponding string
        self.Action_grid = action
        if self.Action_grid == 0:
            Action_grid_agent = "charge"
        elif self.Action_grid == 1:
            Action_grid_agent = "charge_sell"
        elif self.Action_grid == 2:
            Action_grid_agent = "discharge"
        elif self.Action_grid == 3:
            Action_grid_agent = "sell"
        elif self.Action_grid == 4:
            Action_grid_agent = "buy"

        #  compute tje energy surplus
        self.diffProd = self.currentState_panelProd - self.currentState_consumption
        #  compute the temporary battery level. This value can be negative or exceed the battery capacity
        current_battery_temp = self.currentState_battery + (action - 3) * (action - 4) * self.diffProd

        #  define the relu function
        def relu(x):
            return np.maximum(0, x)

        #  define the reward
        # reward_general = -10*relu(-(current_battery_temp-.1*self.batteryCapacity))
        #  reward for charging the battery. It penalizes the agent if the battery is charged too much, over the battery capacity
        reward_charge = -relu(current_battery_temp - self.batteryCapacity) * (action - 1) * (action - 2) * (
                    action - 3) * (action - 4)
        #  reward for charging the battery and selling the surplus energy
        reward_charge_sell = relu(current_battery_temp - self.batteryCapacity) * self.sell_price[
            self.currentState_row] * (
                                 action) * (action - 2) * (action - 3) * (action - 4)
        # reward for discharging the battery. It penalizes the agent if the battery is discharged too much, below 10% of the battery capacity
        #  Add constraint 10 to make sure that the battery is not discharged too much
        reward_discharge = -10 * relu(-(current_battery_temp - .1 * self.batteryCapacity)) * (action) * (action - 1) * (
                    action - 3) * (
                                   action - 4)
        #  reward for selling the surplus energy with selling price
        reward_sell = self.sell_price[self.currentState_row] * relu(self.diffProd) * (action) * (action - 1) * (
                    action - 2) * (action - 4)
        #  reward for buying energy from the grid. It has a negative sign because it is a cost
        reward_buy = -self.currentState_price * relu(-self.diffProd) * (action) * (action - 1) * (action - 2) * (
                    action - 3)
        #  sum all the rewards
        reward = reward_charge + reward_charge_sell + reward_discharge + reward_sell + reward_buy
        #  clip the current battery between 0 and the capacity. This is the real battery level
        self.currentState_battery = np.clip(current_battery_temp, 0, self.batteryCapacity)

        self.currentState_row += 1
        row = self.currentState_row

        self.currentState_price = self.data[row, 3]
        self.currentState_consumption = self.data[row, 4]
        self.currentState_panelProd = self.data[row, 5]

        state1 = self.currentState_battery
        state2 = self.currentState_panelProd
        state3 = self.currentState_consumption
        state4 = self.data_time[self.currentState_row - 1]

        co2_kg = relu(-self.diffProd) * 0.3855535

        self.state = (state1, state2, state3, state4)

        return np.array(self.state, dtype=np.float32), reward, False, dict(dic_diffpro=co2_kg,
                                                                                  dic_battery=self.currentState_battery)

    def reset(self):

        self.state = [self.currentState_battery, self.currentState_panelProd, self.currentState_consumption,
                      self.data_time[self.currentState_row - 1]]

        return np.array(self.state, dtype=np.float32)



