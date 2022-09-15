import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st



x = [1,2,3]
y = [2,3,4]
df = pd.DataFrame(x,y)
plt.plot(x,y)
st.write(fig)
