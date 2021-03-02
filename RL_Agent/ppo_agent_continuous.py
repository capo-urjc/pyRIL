import numpy as np
from RL_Agent.base.PPO_base.ppo_agent_base import PPOSuper
from RL_Agent.base.utils import agent_globals


# worker class that inits own environment, trains on it and updloads weights to global net
class Agent(PPOSuper):
    def __init__(self, actor_lr=1e-4, critic_lr=1e-3, batch_size=32, epsilon=1.0, epsilon_decay=1.0, epsilon_min=0.15,
                 gamma=0.95, n_step_return=10, memory_size=512, loss_clipping=0.2, loss_critic_discount=0.5,
                 loss_entropy_beta=0.001, lmbda=0.95, train_steps=10, exploration_noise=1.0, n_stack=1,
                 img_input=False, state_size=None, net_architecture=None):
        """
        Proximal Policy Optimization (PPO) for continuous action spaces agent class.
        :param actor_lr: (float) learning rate for training the actor NN.
        :param critic_lr: (float) learning rate for training the critic NN.
        :param batch_size: (int) batch size for training procedure.
        :param epsilon: (float) exploration-exploitation rate during training. epsilon=1.0 -> Exploration,
            epsilon=0.0 -> Exploitation.
        :param epsilon_decay: (float) exploration-exploitation rate reduction factor. Reduce epsilon by multiplication
            (new epsilon = epsilon * epsilon_decay)
        :param epsilon_min: (float) min exploration-exploitation rate allowed during training.
        :param gamma: (float) Discount or confidence factor for target value estimation.
        :param n_step_return: (int) Number of steps used for calculating the return.
        :param memory_size: (int) Size of experiences memory.
         :param loss_clipping: (float) Loss clipping factor for PPO.
        :param loss_critic_discount: (float) Discount factor for critic loss of PPO.
        :param loss_entropy_beta: (float) Discount factor for entropy loss of PPO.
        :param lmbda: (float) Smoothing factor for calculating the generalized advantage estimation.
        :param train_steps: (int) Train epoch for each training iteration.
        :param exploration_noise: (float) fixed standard deviation for sample actions from a normal distribution during
            training with the mean proposed by the actor network.
        :param n_stack: (int) Number of time steps stacked on the state (observation stacked).
        :param img_input: (bool) Flag for using a images as states. True state are images (3D array).
        :param state_size: State size. Needed if the original state size is modified by any preprocessing.
        :param net_architecture: (dict) Define the net architecture. Is recommended use dicts from
            RL_Agent.base.utils.networks
        """
        super().__init__(actor_lr=actor_lr, critic_lr=critic_lr, batch_size=batch_size, epsilon=epsilon,
                         epsilon_decay=epsilon_decay, epsilon_min=epsilon_min, gamma=gamma,
                         n_step_return=n_step_return, memory_size=memory_size, loss_clipping=loss_clipping,
                         loss_critic_discount=loss_critic_discount, loss_entropy_beta=loss_entropy_beta, lmbda=lmbda,
                         train_steps=train_steps, exploration_noise=exploration_noise, n_stack=n_stack,
                         img_input=img_input, state_size=state_size, net_architecture=net_architecture)
        self.agent_name = agent_globals.names["ppo_continuous"]

    def build_agent(self, state_size, n_actions, stack=False, action_bound=None):
        """
        Define the agent params, structure, architecture, neural nets ...
        :param state_size: (tuple of ints) State size.
        :param n_actions: (int) Number of actions.
        :param stack: (bool) True means that a sequence of input in contiguous time steps are stacked in the state.
        :param action_bound: ([float]) [min, max]. If action space is continuous set the max and min limit values for
            actions.
        """
        super().build_agent(state_size, n_actions, stack=stack)

        self.action_bound = action_bound
        self.loss_selected = self.proximal_policy_optimization_loss_continuous
        self.actor, self.critic = self._build_model(self.net_architecture, last_activation='tanh')
        self.dummy_action, self.dummy_value = self.dummies_sequential()

    def act_train(self, obs):
        """
        Select an action given an observation in exploration mode.
        :param obs: (numpy nd array) observation (state).
        :return: ([floats], [floats], [float], float) action, one hot action, action probabilities, state value
        """
        obs = self._format_obs_act(obs)
        p = self.actor.predict([obs, self.dummy_value, self.dummy_action, self.dummy_value, self.dummy_value])
        action = action_matrix = p[0] + np.random.normal(loc=0, scale=self.exploration_noise*self.epsilon, size=p[0].shape)
        value = self.critic.predict([obs])[0]
        return action, action_matrix, p, value

    def act(self, obs):
        """
        Select an action given an observation in exploitation mode.
        :param obs: (numpy nd array) observation (state).
        :return: ([floats]) numpy array of float of action shape.
        """
        obs = self._format_obs_act(obs)
        p = self.actor.predict([obs, self.dummy_value, self.dummy_action, self.dummy_value, self.dummy_value])
        action = p[0]
        return action