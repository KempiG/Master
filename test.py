import pandas as pd
import matplotlib.pyplot as plt

x = [1,2,3]
y = [2,3,4]
df = pd.DataFrame(x,y)
plt.plot(df)
