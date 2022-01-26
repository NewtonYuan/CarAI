import sys
import numpy as np
import math
import random
import matplotlib.pyplot as plt

import gym
import game

def simulate():
    learningRate = getLearningRate(0)
    exploreRate = getExploreRate(0)
    discount_factor = 0.99
    totalReward = 0
    totalRewards = []
    threshold = 200
    env.setView(True)
    for episode in range(EPISODE_NUMBER):

        totalRewards.append(totalReward)
        if episode == 2000:
            plt.plot(totalRewards)
            plt.ylabel('rewards')
            plt.show()
            env.memorise('1000')
            break

        obv = env.reset()
        state_0 = state_to_bucket(obv)
        totalReward = 0

        if episode >= threshold:
            exploreRate = 0.01

        for t in range(MAX_TIME):
            action = select_action(state_0, exploreRate)
            obv, reward, done, _ = env.step(action)
            state = state_to_bucket(obv)
            env.remember(state_0, action, reward, state, done)
            totalReward += reward

            # Update the Q based on the result
            best_q = np.amax(q_table[state])
            q_table[state_0 + (action,)] += learningRate * (reward + discount_factor * (best_q) - q_table[state_0 + (action,)])

            # Setting up for the next iteration
            state_0 = state
            env.render()
            if done or t >= MAX_TIME - 1:
                print("Episode %d finished after %i time steps with total reward = %f."
                      % (episode, t, totalReward))
                break
        # Update parameters
        exploreRate = getExploreRate(episode)
        learningRate = getLearningRate(episode)

def load_and_play():
    print("Start loading history")
    history_list = ['30000.npy']

    # load data from history file
    print("Start updating q_table")
    discount_factor = 0.99
    for list in history_list:
        history = load_data(list)
        learningRate = getLearningRate(0)
        print(list)
        file_size = len(history)
        print("file size : " + str(file_size))
        i = 0
        for data in history:
            state_0, action, reward, state, done = data
            best_q = np.amax(q_table[state])
            q_table[state_0 + (action,)] += learningRate * (reward + discount_factor * (best_q) - q_table[state_0 + (action,)])
            if done == True:
                i += 1
                learningRate = getLearningRate(i)

    print("Updating q_table is complete")


    # play game
    env.setView(True)
    reward_count = 0
    for episode in range(EPISODE_NUMBER):
        obv = env.reset()
        state_0 = state_to_bucket(obv)
        totalReward = 0
        for t in range(MAX_TIME):
            action = select_action(state_0, 0.01)
            obv, reward, done, _ = env.step(action)
            state = state_to_bucket(obv)
            totalReward += reward
            best_q = np.amax(q_table[state])
            q_table[state_0 + (action,)] += learningRate * (reward + discount_factor * (best_q) - q_table[state_0 + (action,)])
            state_0 = state
            env.render()
            if done or t >= MAX_TIME - 1:
                print("Episode %d finished after %i time steps with total reward = %f."
                      % (episode, t, totalReward))
                break
        if totalReward >= 1000:
            reward_count += 1
        else:
            reward_count = 0

        if reward_count >= 10:
            env.setView(True)

        learningRate = getLearningRate(i + episode)


def load_and_simulate():
    print("Start loading history")
    history_list = ['30000.npy']

    # load data from history file
    print("Start updating q_table")
    discount_factor = 0.99
    i = 0
    for list in history_list:
        history = load_data(list)
        learningRate = getLearningRate(0)
        print(list)
        file_size = len(history)
        print("file size : " + str(file_size))
        for data in history:
            state_0, action, reward, state, done = data
            env.remember(state_0, action, reward, state, done)
            best_q = np.amax(q_table[state])
            q_table[state_0 + (action,)] += learningRate * (reward + discount_factor * (best_q) - q_table[state_0 + (action,)])
            if done == True:
                i += 1
                learningRate = getLearningRate(i)

    print("Updating q_table is complete")


    # simulate
    env.setView(False)
    for episode in range(EPISODE_NUMBER):
        obv = env.reset()
        state_0 = state_to_bucket(obv)
        totalReward = 0

        if episode > 3000 and episode <= 3010:
            if episode == 3001:
                env.memorise('3000_aft')
            env.setView(True)
        elif episode > 5000 and episode <= 5010:
            if episode == 5001:
                env.memorise('5000_aft')
            env.setView(True)

        for t in range(MAX_TIME):
            action = select_action(state_0, 0.01)
            obv, reward, done, _ = env.step(action)
            state = state_to_bucket(obv)
            env.remember(state_0, action, reward, state, done)
            state_0 = state
            totalReward += reward
            best_q = np.amax(q_table[state])
            q_table[state_0 + (action,)] += learningRate * (reward + discount_factor * (best_q) - q_table[state_0 + (action,)])
            env.render()
            if done or t >= MAX_TIME - 1:
                print("Episode %d finished after %i time steps with total reward = %f."
                      % (episode, t, totalReward))
                break

        learningRate = getLearningRate(i + episode)



def select_action(state, exploreRate):
    if random.random() < exploreRate:
        action = env.action_space.sample()
    else:
        action = int(np.argmax(q_table[state]))
    return action

def getExploreRate(t):
    return max(MIN_exploreRate, min(0.8, 1.0 - math.log10((t+1)/DECAY_FACTOR)))

def getLearningRate(t):
    return max(MIN_learningRate, min(0.8, 1.0 - math.log10((t+1)/DECAY_FACTOR)))

def state_to_bucket(state):
    bucket_indice = []
    for i in range(len(state)):
        if state[i] <= STATE_BOUNDS[i][0]:
            bucket_index = 0
        elif state[i] >= STATE_BOUNDS[i][1]:
            bucket_index = NUM_BUCKETS[i] - 1
        else:
            # Mapping the state bounds to the bucket array
            bound_width = STATE_BOUNDS[i][1] - STATE_BOUNDS[i][0]
            offset = (NUM_BUCKETS[i]-1)*STATE_BOUNDS[i][0]/bound_width
            scaling = (NUM_BUCKETS[i]-1)/bound_width
            bucket_index = int(round(scaling*state[i] - offset))
        bucket_indice.append(bucket_index)
    return tuple(bucket_indice)

def load_data(file):
    np_load_old = np.load
    np.load = lambda *a,**k: np_load_old(*a, allow_pickle=True, **k)
    data = np.load(file)
    np.load = np_load_old
    return data

if __name__ == "__main__":

    env = gym.make("CarAI-v0")
    NUM_BUCKETS = tuple((env.observation_space.high + np.ones(env.observation_space.shape)).astype(int))
    NUM_ACTIONS = env.action_space.n
    STATE_BOUNDS = list(zip(env.observation_space.low, env.observation_space.high))

    MIN_exploreRate = 0.001
    MIN_learningRate = 0.2
    DECAY_FACTOR = np.prod(NUM_BUCKETS, dtype=float) / 10.0
    print(DECAY_FACTOR)

    EPISODE_NUMBER = 9999999
    MAX_TIME = 2000
    #MAX_TIME = np.prod(NUM_BUCKETS, dtype=int) * 100

    q_table = np.zeros(NUM_BUCKETS + (NUM_ACTIONS,), dtype=float)
    simulate()
    #load_and_play()
