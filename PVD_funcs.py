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

def list_ext(uploads, radio3):
    list_ = []
    header_default = ["date [YYYYMMDD]",
                          "time [HHMMSS]",
                          "X [m]",
                          "Y [m]",
                          "Z [m]",
                          "Drain nr. [-]",
                          "Job nr. [-]",
                          "Base unit [-]",
                          "Operator [-]",
                          "Stitcher type [-]",
                          "Stitcher length [m]",
                          "Stitcher ballast [ton]",
                          "Drain type [-]",
                          "Anchoring [-]",
                          "Pattern type [0=square/1=triang.]",
                          "Pattern distance [m]",
                          "Pattern heading [deg]",
                          "Pattern X-position [m]",
                          "Pattern Y-position [m]",
                          "Prescribed depth [m]",
                          "Max. depth [m]",
                          "Pull back [m]",
                          "Cum. drain length [m]",
                          "Duration [s]",
                          "Max. force [kN]",
                          "Stitcher angle [deg]",
                          "ok",
                          "new roll",
                          "canceled",
                          "Log interval [m]",
                          "Data nr. [-]",
                          "Force [kN]"] 
    df_default = pd.DataFrame(columns=header_default)
    
    for file_ in uploads:
        for headerline in file_:
            headerline = str(headerline)
            if '#date' in headerline:
                break
        headerline = headerline[:-3]
        headerlist = headerline.replace("b'#", "").split(',')  
        
        if 'Remarks' in headerlist:
            headerlist.remove('Remarks')
            headerlist.remove('')
            for index, item in enumerate(headerlist):
                if ' [ok' in item:
                    headerlist[index] = 'ok'
                if 'canceled]' in item:
                    headerlist[index] = 'canceled'
                    
        df = pd.read_csv(file_, index_col=False, header=None)
        
        nums = list(range(len(headerlist)))
        headerdict = dict(zip(nums, headerlist))    
        df = df.rename(columns=headerdict)
        df = df.rename(columns={' Drain nr. [-]' : 'Drain nr. [-]'})
        
        force_1_loc = df.columns.get_loc('Force [kN]')
        df_force = df.iloc[:, force_1_loc+1:-1]
        for col in range(len(df_force.columns)):
            df_force = df_force.rename(columns={df_force.columns[col] : f'Force_{col+2}'})
            
        if radio3 == 'Default columns (recommended)':

            if not header_default == headerlist:
                df = pd.concat([df_default, df])

            for col in df.columns:
                if col not in header_default:
                    df = df.drop([col], axis=1)
        elif radio3 == 'Columns from file':
            for col in df.columns:
                if type(col) == int:
                    df = df.drop([col], axis=1)
            
        df = pd.concat([df, df_force], axis=1)
        
        #####
        list_.append(df)
        
    ### Sort list_ on df with most columns ##
    a = max([x.shape[1] for x in list_])
    indexa = [x.shape[1] for x in list_].index(a)
    longest = list_[indexa]
    del list_[indexa]
    list_.insert(0, longest)
    
    return list_, headerlist


def convert(list_, headerlist, wp_calc_method, fixed_nr):
    
    frame = pd.concat(list_, axis=0, ignore_index=True)
    
        ## Rename columns ##
    nums = list(range(len(headerlist)))
    headerdict = dict(zip(nums, headerlist))    
    frame = frame.rename(columns=headerdict)

    frame = frame.sort_values(['Base unit [-]', 'date [YYYYMMDD]', 'time [HHMMSS]'])
    
        ## Add date and time columns ##
    #date_text = frame['date [YYYYMMDD]']
    frame['date [YYYYMMDD]'] = pd.to_datetime(frame['date [YYYYMMDD]'], format='%Y%m%d').dt.date
    frame['time [HHMMSS]'] = frame['time [HHMMSS]'].astype(int)
    for pvd in frame.index:
        if len(str(frame.loc[pvd, 'time [HHMMSS]'])) < 6:
            frame.loc[pvd, 'time [HHMMSS]'] = (6 - len(str(frame.loc[pvd, 'time [HHMMSS]']))) * '0' + str(frame.loc[pvd, 'time [HHMMSS]'])
    time_text = frame['time [HHMMSS]'].copy()
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
    
    tofloat = ['Z [m]',
               'Drain nr. [-]',
               'Max. depth [m]',
               'Max. force [kN]',
               'Prescribed depth [m]',
               'Stitcher angle [deg]']
    
    for col in tofloat:
        if col in frame.columns:
            frame[col] = frame[col].astype(float)
        else:
            continue
    return frame, time_text 
 

def show_delay(frame_filtered, delta, start_time, end_time, date, base_unit):
    
    time_text = frame_filtered['time_text']
    time_text = pd.concat([start_time, time_text, end_time])
    time_text = list(pd.to_datetime(time_text, format='%H%M%S'))

    start = time_text[:-1].copy()
    end = time_text[1:].copy()

    fig, ax = plt.subplots(figsize=[18,3], facecolor='white')
    periods = []
    for pvd in range(len(start)):
        periods.append((start[pvd], end[pvd] - start[pvd]))
    
    periods_op = [tup for tup in periods if tup[1] <= np.timedelta64(int(delta), 's')]
    periods_delay = [tup for tup in periods if tup[1] > np.timedelta64(int(delta), 's')]
    
    ax.broken_barh(
        periods_delay,
        (0.1, 0.2),
        color='#FF6861',
        #edgecolor="black"
    )

    ax.broken_barh(
        periods_op,
        (-0.1, 0.2),
        color='green',
        # edgecolor="black"
    )
    
    ax.set_yticks([0, 0.2])
    ax.set_yticklabels(['Operational', 'Delay'])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.suptitle(f'{date} - {base_unit}', fontsize=20)
    ax.grid(linestyle="--")
    fig.autofmt_xdate()    
    st.write(fig)   

    total_op = total_delay = datetime.timedelta()
    for pvd in periods_op:
        total_op += pvd[1]
    for pvd in periods_delay:
        total_delay += pvd[1]    
    st.write('Operational time: ', str((datetime.datetime.min + total_op).time()))
    st.write('Delay time: ', str((datetime.datetime.min + total_delay).time()))
    
    st.write('Efficiency: ', str(round(100 * total_op.total_seconds() / (total_op.total_seconds() + total_delay.total_seconds()))), '%')
  
    fn = f'{date} - {base_unit}.png'
    img = io.BytesIO()
    plt.savefig(img, format='png')
     
    st.download_button(
       label='Download as image',
       data=img,
       file_name=fn,
       mime='image/png'
    )   
    
  
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
    
    
    choose_scale = st.selectbox('Choose plot parameter:',
                         scale,
                         help='Choose from the list what you want to plot in the figure below', index=8)
    
    frame.columns[10] == choose_scale
    if choose_scale in frame.columns:
        fig = px.scatter(data_frame = frame,
                         x=frame['X [m]'],
                         y=frame['Y [m]'],
                         color=choose_scale, 
                         color_continuous_scale='turbo')
                         
        fig.update_yaxes(scaleanchor='x', scaleratio=1)
        st.write(fig)
    else:
        st.write(f'{choose_scale} not found')
    
    # from streamlit_plotly_events import plotly_events
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

    
    
