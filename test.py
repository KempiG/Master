import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


st.write("My First Streamlit Web App")
x = [1,2,3,5,1,2,2,4]
y = [2,3,4,2,5,7,4,2]
df = pd.DataFrame(x,y)
df=df.set_axis(['X','Y'],axis=1,inplace=True)

st.write(df)


fig = plt.figure()
ax = fig.add_subplot(1,1,1)
plt.scatter(x,y,color='r')
plt.title('Dit is een testafbeelding')
plt.xlabel('x')
plt.ylabel('y')
st.write(fig)
