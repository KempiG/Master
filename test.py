import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st



x = [1,2,3,5,1,8,2,4]
y = [2,3,4,2,5,7,4,2]
df = pd.DataFrame(x,y)

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
plt.scatter(df)
plt.title('Dit is een testafbeelding')
plt.xlabel('x')
plt.ylabel('y')
st.write(fig)
