Here are some results of tuning different ML methods from sklearn:
from the following class sklearn.svm.SVC
and from sklearn.linear_model.SGDClassifier

common condition: number of samples=5000
These are not final results since we will use all 40k samples later on. These meant to tune better the parameters
(the are 40k samples)

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

Having a word or a phrase prominent is simply emphasizing a certain syllable sequence in a sentence. On an every day life prominenting words during a conversation helps convey massages better due to the fact that it enables to draw the attention to the emphasized syllables. This goal can be acheived similarly when synthesizing a speech signal in a TTS system, while here the information on prosody change, and pitch accent modifications is done in an automatic fashion. In this talk I will describe the process of training a pitch accent predictor by using swbd nxt corpus as a tool to determine word prominence














