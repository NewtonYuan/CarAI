import gym
from gym import spaces
import numpy as np
from game.envs.game import CarAI

class CarAIEnv(gym.Env):
    metadata = {'render.modes' : ['human']}
    def __init__(self):
        print("init")
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(np.array([0, 0, 0, 0, 0]), np.array([10, 10, 10, 10, 10]), dtype=np.int)
        self.is_view = True
        self.pyrace = CarAI(self.is_view)
        self.memory = []

    def step(self, action):
        self.pyrace.action(action)
        reward = self.pyrace.evaluate()
        done = self.pyrace.finished()
        obs = self.pyrace.observe()
        return obs, reward, done, {}

    def setView(self, flag):
        self.is_view = flag

    def render(self, mode="human", close=False):
        if self.is_view:
            self.pyrace.view()

    def reset(self):
        del self.pyrace
        self.pyrace = CarAI(self.is_view)
        obs = self.pyrace.observe()
        return obs

    def memorise(self, file):
        np.save(file, self.memory)
        print(file + " saved")

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
