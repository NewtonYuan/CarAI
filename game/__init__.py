from gym.envs.registration import register

register(
    id='CarAI-v0',
    entry_point='game.envs:CarAIEnv',
    max_episode_steps=50000000,
)
