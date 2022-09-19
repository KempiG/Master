# -*- coding: utf-8 -*-
"""
Created on Mo 12 Sept  2 13:15:51 2022

@author: FKAM
"""

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go
#import altair as alt
#from bokeh.plotting import figure


def convert(list_, headerlist, wp_calc_method, fixed_nr):
    
    frame = pd.concat(list_, axis=0, ignore_index=True)
    
        ## Rename columns ##
    nums = list(range(len(headerlist)))
    headerdict = dict(zip(nums, headerlist))    
    frame = frame.rename(columns=headerdict)

    frame = frame.sort_values(['Base unit [-]', 'date [YYYYMMDD]', 'time [HHMMSS]'])
    
        ## Add date and time columns ##
    frame['date [YYYYMMDD]'] = pd.to_datetime(frame['date [YYYYMMDD]'], format='%Y%m%d').dt.date
    frame['time [HHMMSS]'] = frame['time [HHMMSS]'].astype(int)
    for pvd in frame.index:
        if len(str(frame.loc[pvd, 'time [HHMMSS]'])) < 6:
            frame.loc[pvd, 'time [HHMMSS]'] = (6 - len(str(frame.loc[pvd, 'time [HHMMSS]']))) * '0' + str(frame.loc[pvd, 'time [HHMMSS]'])
    frame['time [HHMMSS]'] = pd.to_datetime(frame['time [HHMMSS]'], format='%H%M%S').dt.time

        ## Cable tension + wp thickness ##
    if wp_calc_method == 'No':
        wp_frame = 0
    else:
        wp_thickness = [100]*len(frame)
        
        for pvd in range(len(frame)):
            
            keys = list(frame)
            force1 = keys.index('Force [kN]')
            force_df = frame.iloc[:, force1:]
            force_pvd =  force_df.loc[pvd,:].values.tolist()
            
            force_pvd = [i for i in force_pvd if i != 0]    #remove zeros
            force_pvd = force_pvd[2:-3]                     #remove first 2 and last 2 values
            
            if len(force_pvd) > 0:
                cable_tension = min(force_pvd)
                if wp_calc_method == 'Lowest force plus fixed number':
                    cutoff = cable_tension + fixed_nr
                elif wp_calc_method == 'Manual choice':
                    cutoff = fixed_nr
                else:
                    cutoff = 0
                    
                cable_tension_index = force_pvd.index(cable_tension)
                force_pvd = force_pvd[:cable_tension_index]
                        
                wp = (sum(i > cutoff for i in force_pvd) + 2) * frame['Log interval [m]'][pvd]
                wp_thickness[pvd] = wp
        
        wp_frame = frame[['X [m]', 'Y [m]']]
        wp_frame['wp [m]'] = wp_thickness
        
        wp_frame['csx'] = [528374]*len(frame)
        wp_frame['csy'] = [507360]*len(frame)
        
    frame['Z [m]'] = frame['Z [m]'].astype(float)
    frame['Drain nr. [-]'] = frame['Drain nr. [-]'].astype(float)
    frame['Max. depth [m]'] = frame['Max. depth [m]'].astype(float)
    frame['Max. force [kN]'] = frame['Max. force [kN]'].astype(float)    
    frame['Prescribed depth [m]'] = frame['Prescribed depth [m]'].astype(float)
    frame['Stitcher angle [deg]'] = frame['Stitcher angle [deg]'].astype(float)
    
    return frame, wp_frame

# from streamlit_plotly_events import plotly_events

def show_preview(frame):
    scale = ["date [YYYYMMDD]",
                          "time [HHMMSS]",
                          "Z [m]",
                          "Drain nr. [-]",
                          "Base unit [-]",
                          "Operator [-]",
                          "Stitcher type [-]",
                          "Prescribed depth [m]",
                          "Max. depth [m]",
                          "Max. force [kN]",
                          "Stitcher angle [deg]"] 
    
    st.write('**Preview:**')
    choose_scale = st.selectbox('Choose plot parameter:',
                         scale,
                         help='Choose from the list what you want to plot in the figure below', index=8)
     
    Max_depth_color = frame['Max. depth [m]']
    st.write(Max_depth_color)
        
    fig = px.scatter(data_frame = frame,
                     x=frame['X [m]'],
                     y=frame['Y [m]'],
                     color=choose_scale, 
                     color_continuous_scale='turbo')
    
    
    
    # trial
    temp_options = range(1,25)
    temp = st.select_slider("Choose a range", options=temp_options)
    st.write("The range is",temp)

                     
    fig.update_yaxes(scaleanchor='x', scaleratio=1)
    st.write(fig)
    # clickedPoint = plotly_events(fig, key="line")
    # st.write(f"Clicked Point: {clickedPoint}")
        
    
    
def show_wp(wp_frame, cs):
    # st.write('**Working platform thickness:**')
    # #fig1 = go.Figure()
    # fig1 = px.scatter(data_frame = wp_frame,
    #                  x=wp_frame['X [m]'],
    #                  y=wp_frame['Y [m]'],
    #                  color='wp [m]', 
    #                  color_continuous_scale='turbo',
    #                  range_color=[0,5])
                     
    # fig1.update_yaxes(scaleanchor='x', scaleratio=1)
    # st.write(fig1)
    
    st.write('**Working platform thickness:**')
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=wp_frame['X [m]'], 
                              y=wp_frame['Y [m]'], 
                              mode='markers', 
                              name='PVD points',
                              marker_color=wp_frame['wp [m]']))

    x = [507360, 507460]
    y = [cs, cs]
    fig1.add_trace(go.Scatter(x=x, y=y, 
                              mode='lines',
                              name='Cross section'))
    
    fig1.update_yaxes(scaleanchor='x', scaleratio=1)
    st.write(fig1)
    

    #st.write(fig1)
    # fig3 = go.Figure(data=fig1.data + fig2.data)
    # st.write(fig3)

    
    
    
# def show_preview_altair(frame):
#     st.write('**Preview:**')
#     plotframe = frame[['X [m]', 'Y [m]', 'Max. depth [m]']].copy()    
#     plotframe = plotframe.rename(columns={'X [m]': 'X',
#                                           'Y [m]': 'Y',
#                                           'Max. depth [m]': 'Max_depth'})

#     a = alt.Chart(plotframe).mark_circle().encode(alt.X('X', 
#                                                         scale=alt.Scale(domain=(plotframe['X'].min(), 
#                                                                                      plotframe['X'].max()))), 
#                                                   alt.Y('Y',
#                                                         scale=alt.Scale(domain=(plotframe['Y'].min(), 
#                                                                                      plotframe['Y'].max()))),
#                                                   color=alt.Color('Max_depth', scale=alt.Scale(scheme='turbo'))).interactive()
    
#     st.altair_chart(a, use_container_width=True)

# def show_preview_bokeh(frame):
#     st.write('**Preview:**')
#     plotframe = frame[['X [m]', 'Y [m]', 'Max. depth [m]']].copy()    
#     plotframe = plotframe.rename(columns={'X [m]': 'X',
#                                           'Y [m]': 'Y',
#                                           'Max. depth [m]': 'Max_depth'})    
#     p = figure(title='simple line example', 
#                x_axis_label='X',
#                y_axis_label='Y',
              
#                match_aspect=True)
#     p.circle(source=plotframe, x='X', y='Y')
#     st.bokeh_chart(p, use_container_width=True)
    
