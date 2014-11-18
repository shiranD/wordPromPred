The training is performed in 'training.py' found in the src.
So far the best result was acheived by linear kernal svm to be 0.8 accuracy.
common condition: number of samples=5k (there are 40k samples)
These are not final results since we will use all 40k samples later on. These helped tune better the parameters


Kernel=RBF
C=100, gamma=0,   0.792
C=1,   gamma=0.1, 0.78
C=1,   gamma=0.1, 0.721
C=100, gamma=10,  0.72

Kernel=Linear
C=1,   gamma=0,    0.801
C=1,   gamma=0.1,  0.801
C=1,   gamma=0.01, 0.801
C=100, gamma=0,    0.78

Kernel=Poly
C=1, gamma=0,    degree=3, 0.721
C=1, gamma=0,    degree=4, 0.721
C=1, gamma=0.1,  degree=4, 0.776
C=1, gamma=0.01, degree=4, 0.721

kernel=Sig
C=1,   gamma=0,   coef=1, 0.721
C=100, gamma=0,   coef=1, 0.721
C=1,   gamma=0.1, coef=1, 0.714
C=1,   gamma=0,   coef=1  0.721

SGD with loss='hinge'
alpha=10^(-4), 0.773
alpha=10^(-5), 0.77
alpha=10^(-3), 0.789
alpha=10^(-2), 0.742
alpha=10^(-1), 0.791

SGD with loss='log'
alpha=10^(-4), 0.774
alpha=10^(-5), 0.773
alpha=10^(-3), 0.792
alpha=10^(-2), 0.738
alpha=10^(-1), 0.787

SGD with loss='perceptron'
alpha=10^(-4), 0.759
alpha=10^(-3), 0.764
alpha=10^(-2), 0.777
alpha=10^(-1), 0.765

Here is the abstract I thought about our project as a brief for the seminar talk.

Having a word or a phrase prominent is simply emphasizing a certain syllable sequence in a sentence. On an every day life ‘voice highlighting’ words during a conversation helps convey massages better due to the fact that it enables to draw the attention to the emphasized syllables. This goal can be achieved similarly when synthesizing a speech signal in a TTS system, while here the decision on pitch accent modifications, reflecting prominence, is done in an automatic fashion. In this talk I will describe the process of training a pitch accent predictor by using swbd nxt corpus to determine word prominence.

Here are things I would like to talk about during our meeting.
contribution
ssh public key
gitlab on bigbird
to ask about presentation 
no sleep no hangup on osx








