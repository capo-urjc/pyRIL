# import tensorflow as tf
# import tensorflow.compat.v1 as tf
# tf.disable_v2_behavior()
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Conv2D, Conv1D, Flatten, MaxPooling2D, Dropout, Lambda, Input, Concatenate, Reshape, BatchNormalization, SimpleRNN, LSTM
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import backend as K
import numpy as np
import random
import numbers


class DiscriminatorBase(object):
    def __init__(self, scope, state_size, n_actions, n_stack=1, img_input=False, use_expert_actions=True,
                 learning_rate=1e-3, batch_size=5, epochs=5, val_split=0.15, discrete=False, preprocess=None,
                 tensorboard_dir=None):

        self.use_expert_actions = use_expert_actions

        self.state_size = state_size
        self.n_actions = n_actions

        self.img_input = img_input
        self.n_stack = n_stack
        self.stack = self.n_stack > 1
        self.learning_rate = learning_rate

        self.batch_size = batch_size
        self.epochs = epochs
        self.val_split = val_split

        self.discrete_actions = discrete
        self.preprocess = preprocess
        self.global_epochs = 0
        self.tensorboard_dir = tensorboard_dir
        self.discriminator_builded = False

    def _build_model(self, net_architecture):
        # Neural Net for Deep-Q learning Model
        if self.img_input:
            state_size = (*self.state_size[:2], self.state_size[-1] * self.n_stack)
        elif self.n_stack is not None and self.n_stack > 1:
            state_size = (self.n_stack, self.state_size)
        else:
            state_size = (self.state_size,)

        self.discriminator_builded = True
        return self._build_net(state_size, net_architecture)

    def _build_net(self, state_size, net_architecture):
        pass

    def get_reward(self, obs, action, parallel=False):
        if parallel:
            if self.discrete_actions:
                # If not one hot encoded
                onehot = False
                if hasattr(action[0], 'shape'):
                    if len(action[0].shape) > 0:
                        onehot = action[0].shape[0] > 1
                if not onehot:
                    action_matrix = np.array([np.zeros(self.n_actions) for a in action])
                    for a, a_m in zip(action, action_matrix):
                        a_m[a] = 1
                    action = action_matrix

            action = np.array(action)
            if self.img_input:
                if self.stack:
                    if np.array(obs[0]).shape != (*self.state_size[0:-1], self.state_size[-1] * self.n_stack):
                        obs = np.array([np.dstack(o) for o in obs])
                    else:
                        obs = np.array(obs)
                else:
                    aaa = np.array(obs[0]).shape
                    eee = self.state_size
                    if np.array(obs[0]).shape != self.state_size:
                        # obs = np.array([obs[:, :, -self.state_size[-1]]])
                        obs = np.array(obs[:, :, :, -self.state_size[-1]])
                        if self.state_size[-1] == 1:
                            obs = obs[:, :, :, np.newaxis]
                    else:
                        obs = np.array(obs)
            elif self.stack:
                # obs = np.transpose(obs)
                # obs = np.reshape(obs, (1, self.state_size, self.n_stack))
                obs = np.array(obs)
            else:
                # If inputs are stacked but nor the discriminator, select the las one input from each stack
                if len(obs.shape) > 2:
                    obs = obs[:, -1, :]  # cambiar por obs[:, -1] si funciona para más formas de datos
                obs = np.array(obs)

            reward = self.predict(obs, action)
            reward = np.squeeze(reward)
            return reward
        else:
            if self.discrete_actions:
                # If not one hot encoded
                # onehot = False
                # if hasattr(action, 'shape'):
                #     onehot = action.shape[0] > 1
                onehot = not isinstance(action, numbers.Integral)
                if not onehot:
                    action_matrix = np.zeros(self.n_actions)
                    action_matrix[action] = 1
                    action = action_matrix

            action = np.array([action])
            if self.img_input:
                if self.stack:
                    if np.array(obs).shape != (*self.state_size[0:-1], self.state_size[-1]*self.n_stack):
                        obs = np.array([np.dstack(obs)])
                    else:
                        obs = np.array([obs])
                else:
                    if np.array(obs).shape != self.state_size:
                        obs = np.array([obs[:, :, -self.state_size[-1]]])
                        if self.state_size[-1] == 1:
                            obs = obs[:, :, :, np.newaxis]
                    else:
                        obs = np.array([obs])
            elif self.stack:
                # obs = np.transpose(obs)
                # obs = np.reshape(obs, (1, self.state_size, self.n_stack))
                obs = np.array([obs])
            else:
                # If inputs are stacked but nor the discriminator, select the las one input from each stack

                if len(obs.shape) > 1:
                    obs = obs[-1, :]

                obs = np.array([obs])


            reward = self.predict(obs, action)[0]
            # reward2 = self.sess.run(self.reward2, feed_dict={self.expert_traj_s: obs,
            #                                                  self.expert_traj_a: action})[0]
            # print('Reward_1: ', reward, 'reward_2: ', reward2)
        return reward

    def predict(self, obs, action):
        pass

    # def train(self, expert_s, expert_a, agent_s, agent_a):
    def train(self, expert_traj, agent_traj):
        print("Training discriminator")

        # Formating network input
        if self.use_expert_actions:
            if self.img_input:
                if self.stack:
                    expert_traj_s = [np.dstack(x[0]) for x in expert_traj]

                    # eee = expert_traj_s[0].shape
                    # aaa = agent_traj[0][0].shape
                    if expert_traj_s[0].shape != agent_traj[0][0].shape:
                        agent_traj_s = [np.dstack(x[0]) for x in agent_traj]
                    else:
                        agent_traj_s = [x[0] for x in agent_traj]
                else:
                    expert_traj_s = [np.array(x[0]) for x in expert_traj]
                    # eee = expert_traj_s[0].shape
                    # aaa = agent_traj[0][0].shape
                    if expert_traj_s[0].shape != agent_traj[0][0].shape:
                        if self.state_size[-1] > 1:
                            agent_traj_s = [np.array(x[0][:, :, -self.state_size[-1]]) for x in agent_traj]
                        else:
                            agent_traj_s = [np.array(x[0][:, :, -self.state_size[-1]])[:, :, np.newaxis] for x in
                                            agent_traj]
                    else:
                        agent_traj_s = [np.array(x[0]) for x in agent_traj]

            elif self.stack:
                expert_traj_s = [np.array(x[0]) for x in expert_traj]
                agent_traj_s = [np.array(x[0]) for x in agent_traj]

            else:
                agent_traj_s = [x[0] for x in agent_traj]
                # If inputs are stacked but nor the discriminator, select the las one input from each stack
                if len(agent_traj_s[0].shape) > 1:
                    agent_traj_s = [x[-1, :] for x in agent_traj_s]
                expert_traj_s = [x[0] for x in expert_traj]

            expert_traj_a = [x[1] for x in expert_traj]
            agent_traj_a = [x[1] for x in agent_traj]
        else:
            if self.img_input:
                if self.stack:
                    expert_traj_s = [np.dstack(x) for x in expert_traj]

                    # eee = expert_traj_s[0].shape
                    # aaa = agent_traj[0][0].shape
                    if expert_traj_s[0].shape != agent_traj[0][0].shape:
                        agent_traj_s = [np.dstack(x[0]) for x in agent_traj]
                    else:
                        agent_traj_s = [x[0] for x in agent_traj]
                else:
                    expert_traj_s = np.array(expert_traj)
                    # eee = expert_traj_s[0].shape
                    # aaa = agent_traj[0][0].shape
                    if expert_traj_s[0].shape != agent_traj[0][0].shape:
                        if self.state_size[-1] > 1:
                            agent_traj_s = [np.array(x[0][:, :, -self.state_size[-1]]) for x in agent_traj]
                        else:
                            agent_traj_s = [np.array(x[0][:, :, -self.state_size[-1]])[:, :, np.newaxis] for x in
                                            agent_traj]
                    else:
                        agent_traj_s = [np.array(x[0]) for x in agent_traj]

            elif self.stack:
                expert_traj_s = np.array(expert_traj)
                agent_traj_s = np.array(agent_traj)

            else:
                agent_traj_s = [x[0] for x in agent_traj]
                # If inputs are stacked but nor the discriminator, select the las one input from each stack
                if len(agent_traj_s[0].shape) > 1:
                    agent_traj_s = [x[-1, :] for x in agent_traj_s]
                expert_traj_s = np.array(expert_traj)

            expert_traj_a = None
            agent_traj_a = None

        # Take the same number of samples of each class
        n_samples = min(len(expert_traj), len(agent_traj))
        # expert_traj_index = np.array(random.sample(range(len(expert_traj)), n_samples))
        # agent_traj_index = np.array(random.sample(range(len(agent_traj)), n_samples))

        expert_traj_index = np.array(np.random.choice(len(expert_traj), size=n_samples, replace=False))
        agent_traj_index = np.array(np.random.choice(len(agent_traj), size=n_samples, replace=False))

        expert_traj_s = np.array(expert_traj_s)[expert_traj_index]
        agent_traj_s = np.array(agent_traj_s)[agent_traj_index]

        if self.use_expert_actions:
            expert_traj_a = np.array(expert_traj_a)[expert_traj_index]
            agent_traj_a = np.array(agent_traj_a)[agent_traj_index]

            if self.discrete_actions:
                # If agent actions are not one hot encoded
                if len(agent_traj_a.shape) < 2:
                    one_hot_agent_a = []
                    for i in range(agent_traj_a.shape[0]):
                        action_matrix_agent = np.zeros(self.n_actions)
                        action_matrix_agent[agent_traj_a[i]] = 1
                        one_hot_agent_a.append(action_matrix_agent)
                    agent_traj_a = np.array(one_hot_agent_a)

                # If expert actions are not one hot encoded
                if len(expert_traj_a.shape) < 2:
                    one_hot_expert_a = []
                    for i in range(expert_traj_a.shape[0]):
                        action_matrix_expert = np.zeros(self.n_actions)
                        action_matrix_expert[expert_traj_a[i]] = 1
                        one_hot_expert_a.append(action_matrix_expert)
                    expert_traj_a = np.array(one_hot_expert_a)

        loss = self.fit(expert_traj_s, expert_traj_a, agent_traj_s, agent_traj_a,
                                        batch_size=self.batch_size, epochs=self.epochs, validation_split=self.val_split)
        return loss

    def fit(self, expert_traj_s, expert_traj_a, agent_traj_s, agent_traj_a, batch_size=128, epochs=10,
            validation_split=0.10):
        loss = self.model.fit(expert_traj_s, agent_traj_s, expert_traj_a, agent_traj_a, batch_size=batch_size,
                              epochs=epochs, shuffle=True, verbose=2, validation_split=validation_split)

        if validation_split > 0.:
            return [loss.history['loss'][-1], loss.history['acc'][-1]], [loss.history['val_loss'][-1], loss.history['val_acc'][-1]]
        else:
            return [loss.history['loss'][-1], loss.history['acc'][-1]]
