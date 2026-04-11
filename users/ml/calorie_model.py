import numpy as np
from sklearn.linear_model import LinearRegression

# Example training data
# age, weight, height, activity → calories
X = np.array([
    [25,70,175,1.2],
    [30,80,180,1.55],
    [22,60,165,1.375],
    [35,90,185,1.725],
    [28,75,170,1.55],
    [40,85,178,1.2],
])

y = np.array([
    2000,
    2600,
    1900,
    3000,
    2400,
    2200
])

model = LinearRegression()
model.fit(X,y)

def predict_calories(age, weight, height, activity):

    data = np.array([[age, weight, height, activity]])

    prediction = model.predict(data)

    return int(prediction[0])