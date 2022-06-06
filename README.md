# pyRIL (Python Reinforcement and Imitation Learning Library)
## Install

This library has been tested on Python 3.7 and TensorFlow 2.2.  
We provide two installation option depending on the use of TensorFlow with CPU or GPU.

### TensorFlow CPU

A requirements.txt file is provide with the minimum required dependencies.
complete_requirements.txt include an extended list of dependencies in case that requirements.txt where not enough.

If tensorflow is not working on GPU try to install it through:
```bash
pip install tensorflow-gpu==2.2
```

We include some jupyter notebooks tutorials on how to use the library. These tutorials are ordered and increasingly 
include the most important features of this library. To run these tutorials you should install additionally Jupyter Notebook.

Some environments used in some tutorials, like LunarLander and Atari games, occasionally raise some errors related with the gym library installation. In this case try to install gym following the instructions bellow:
```bash
pip install swig
pip install gym
pip install gym[Box2D]
pip install gym[atari]
```
