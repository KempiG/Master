# -*- coding: utf-8 -*-
"""
Created on Tue May 11 17:47:49 2021

@author: KALT
"""
import pandas as pd
import streamlit as st
from PIL import Image
import CDC_funcs
import CRC_funcs
import PVD_funcs

st.set_page_config(layout="wide")
#st.markdown('<style>body{background-color: #D1D1D1;}</style>',unsafe_allow_html=True)

header1, header2 = st.columns([1,5])
image1 = Image.open('Cofra_logo.PNG')
header1.image(image1, width=100)

def main():
    
    technique = st.sidebar.radio("""Choose technique""", ['CDC', 'CRC', 'PVD'])
    
    #####CDC#####
    if technique == 'CDC':
        header2.title("""CDC data import""")

        uploads = st.sidebar.file_uploader('Upload log files', 
                                           accept_multiple_files=True, 
                                           type='log')
        radio1 = st.sidebar.radio('Remove points with less than 3 blows?', ['yes','no'])
        radio2 = st.sidebar.radio('Save as?', ['Excel file','CSV file'])        
        

        if len(uploads) == 1:
            st.write(f' **{len(uploads)}** file imported')
        else:
            st.write(f' **{len(uploads)}** files imported')
        
        if len(uploads) > 0:
            list_ = []
            for file_ in uploads:
                ##### only for new file type
                headers = [0,1]
                df = pd.read_csv(file_, skiprows=headers, index_col=False, usecols=(range(76)), header=None)
                #####
                list_.append(df)
                
            new_name = uploads[0].name
            new_name=new_name.split('_')
            new_name=new_name[0]
            
            col1, col2 = st.columns([2,4])
            start_button = col1.button('Process .log files', key='1')
            
            text = '''
                        
                ---
                
                '''
            st.markdown(text)
            
            if start_button:
                with st.spinner(text='In progress...'):
                    frame = CDC_funcs.convert(list_, radio1, radio2, new_name)    
                
                    if radio2 == 'CSV file':
                        tmp_download_link = CDC_funcs.download_link_csv(frame, 
                                                                        f'{new_name}.csv', 
                                                                        'Click here to download CSV file!')
                    elif radio2 == 'Excel file':
                        tmp_download_link = CDC_funcs.download_link_excel(frame, 
                                                                          f'{new_name}.xlsx', 
                                                                          'Click here to download excel file!')
                    st.markdown(tmp_download_link, unsafe_allow_html=True)                    
                    
                text = '''
                        
                ---
                
                '''
                st.markdown(text)
                
                CDC_funcs.show_preview(frame)
                st.success('Done!')
                
    #####CRC#####
    elif technique == 'CRC':
        header2.title("""CRC data import""")
        
        uploads_ext = st.sidebar.file_uploader('Upload pos files', 
                                               accept_multiple_files=True, 
                                               type='ext')
        uploads_log = st.sidebar.file_uploader('Upload log files', 
                                               accept_multiple_files=True, 
                                               type='log')        
        radio1 = st.sidebar.radio('Save as?', ['Excel file','CSV file'])
        
        uploads_pos = []
        uploads_acc = []

        if len(uploads_ext) > 0:
            for ext_file in uploads_ext:
                if 'pos' in ext_file.name:
                    uploads_pos.append(ext_file)
                elif 'acc' in ext_file.name:
                    uploads_acc.append(ext_file)
                    
        if len(uploads_pos) == 1:
            st.write(f' **{len(uploads_pos)}** pos file imported')
        else:
            st.write(f' **{len(uploads_pos)}** pos files imported')
        if len(uploads_acc) == 1:
            st.write(f' **{len(uploads_acc)}** acc file imported')
        else:
            st.write(f' **{len(uploads_acc)}** acc files imported')                
        if len(uploads_log) == 1:
            st.write(f' **{len(uploads_log)}** log file imported')
        else:
            st.write(f' **{len(uploads_log)}** log files imported')        
        
        if len(uploads_ext) > 0:
            
            if len(uploads_pos) < len(uploads_acc):
                num_missing = len(uploads_acc) - len(uploads_pos)
                st.warning(f'**WARNING: You are missing {num_missing} pos files, number of pos and acc files should be equal**')
            elif len(uploads_acc) < len(uploads_pos):
                num_missing = len(uploads_pos) - len(uploads_acc)
                st.warning(f'**WARNING: You are missing {num_missing} acc files, number of pos and acc files should be equal**')
            
            select_headers = st.multiselect('Add/remove columns', 
                                             ['Date', 'Time','Acceleration','Direction [deg]', 'X','Y', 'Pass', 'Speed [km/h]'], 
                                             ['Date', 'Time','Acceleration','Direction [deg]', 'X','Y', 'Pass', 'Speed [km/h]'])    
            
            log_ = []
            pos_ = []
            acc_ = []
            
            if len(uploads_log) > 0:
                log_present = True
            else:
                log_present = False
                st.warning('**WARNING: no log files uploaded, driving speed cannot be calculated**')
            
            if len(uploads_acc) > 0:
                acc_present = True
            else:
                acc_present = False

            if log_present:
                for log_file in uploads_log:
                    df = pd.read_csv(log_file, skiprows=[0], index_col=False)
                    log_.append(df)
            for pos_file in uploads_pos:
                df = pd.read_csv(pos_file, skiprows=[0], index_col=False)
                pos_.append(df)
            if acc_present:
                for acc_file in uploads_acc:
                    df = pd.read_csv(acc_file, skiprows=[0,1], index_col=False, header=None)
                    acc_.append(df)
            
            start_button = st.button('Process files', key='1')
            
            text = '''
                    
            ---
            
            '''
            st.markdown(text)            
            
            if start_button:
                with st.spinner(text='In progress...'):
                    output, pos, acc, log = CRC_funcs.convert(pos_, acc_, log_, log_present, acc_present, select_headers)
                    
                    if radio1 == 'CSV file':
                        download_link_proc = CDC_funcs.download_link_csv(output, 
                                                                          'CRC_data_processed.csv', 
                                                                          'Click here to download processed data')
                        download_link_pos = CDC_funcs.download_link_csv(pos, 
                                                                          'CRC_data_pos.csv', 
                                                                          'Click here to download raw pos data')
                        download_link_acc = CDC_funcs.download_link_csv(acc, 
                                                                          'CRC_data_acc.csv', 
                                                                          'Click here to download raw acc data')
                        download_link_log = CDC_funcs.download_link_csv(log, 
                                                                          'CRC_data_log.csv', 
                                                                          'Click here to download raw log data')                        
                    elif radio1 == 'Excel file':
                        download_link_proc = CDC_funcs.download_link_excel(output, 
                                                                          'CRC_data_processed.xlsx', 
                                                                          'Click here to download processed data!')
                        download_link_pos = CDC_funcs.download_link_excel(pos, 
                                                                          'CRC_data_pos.xlsx', 
                                                                          'Click here to download raw pos data')
                        download_link_acc = CDC_funcs.download_link_excel(acc, 
                                                                          'CRC_data_acc.xlsx', 
                                                                          'Click here to download raw acc data')

                        download_link_log = CDC_funcs.download_link_excel(log, 
                                                                          'CRC_data_log.xlsx', 
                                                                          'Click here to download raw log data')                        
                        
                    st.write('**Processed data:**')
                    st.markdown(download_link_proc, unsafe_allow_html=True)                    
                    st.write('**Raw data:**')     
                    st.markdown(download_link_pos, unsafe_allow_html=True)
                    st.markdown(download_link_acc, unsafe_allow_html=True)
                    if log_present:
                        st.markdown(download_link_log, unsafe_allow_html=True)
                     
                text = '''
                        
                ---
                
                '''
                st.markdown(text)
                
                CRC_funcs.show_preview(output)
                st.success('Done!')
    
    #####PVD#####
    elif technique == 'PVD':
        header2.title("""PVD data import""")
        #col1, col2 = st.columns(2)
        uploads = st.sidebar.file_uploader('Upload log files', 
                                           accept_multiple_files=True, 
                                           type='ext',
                                           help="""Select one or multiple EXT files with PVD data""")                
        radio1 = st.sidebar.radio('Save as?', ['Excel file','CSV file'])
        #radio2 = st.sidebar.radio('Show platform thickness map?', ['No', 'Yes'])
        
        # if radio2 == 'Yes':
        #     wp_select = st.sidebar.selectbox('Choose method to calculate cable tension', 
        #                                  ('Lowest force plus fixed number','Manual choice'))
        #     if wp_select == 'Lowest force plus fixed number':
        #         fixed_nr = st.sidebar.number_input('Fixed number',
        #                                          value = 5,
        #                                          step = 1)
        #     elif wp_select == 'Manual choice':
        #         fixed_nr = st.sidebar.number_input('Cutoff force between working platform and soft soil',
        #                                            value = 50,
        #                                            step = 1)
        # elif radio2 == 'No':
        #     wp_select = 'No'
        #     fixed_nr = 'No'
        wp_select = 'No'
        fixed_nr = 'No'
        
        radio3 = st.sidebar.radio('Which columns?', 
                                  ['Default columns (recommended)', 'Columns from file'],
                                  help="""**Default columns:** The output file will always contain the same columns
                                  independent of the columns in the uploaded EXT files  
                                  **Columns from file:**
                                  The output file will contain all the columns in the uploaded EXT files, 
                                  note that this can differ based on the CMS version""")
                                
        if len(uploads) == 1:
            st.write(f' **{len(uploads)}** file imported')
        else:
            st.write(f' **{len(uploads)}** files imported')
            
        if len(uploads) > 0:
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
                        
            col1, col2 = st.columns([2,4])
            
            if 'bool' not in st.session_state:
                st.session_state.bool = False            
            
            start_button = col1.button('Start processing / Reset')
                  
            if start_button:
                st.session_state.bool = not st.session_state.bool
                        
            text = '''
                        
            ---
            
            '''
            st.markdown(text)
            
            if st.session_state.bool:
                with st.spinner(text='In progress...'):
                    frame, wp_frame = PVD_funcs.convert(list_, headerlist, wp_select, fixed_nr)
                    
                    ## Output on screen ##    
                    col1, col2, col3 = st.columns(3)
                    col1.metric('Number of drains [-]', len(frame))
                    col2.metric('Linear meter [m]', round(frame['Max. depth [m]'].sum(),2))
                    col3.metric('Average installation depth [m]', round(frame['Max. depth [m]'].mean(),2))
                    
                    ## Download link ##
                    if radio1 == 'CSV file':
                        tmp_download_link = CDC_funcs.download_link_csv(frame, 
                                                                        'PVD_data_processed.csv', 
                                                                        'Click here to download CSV file!')
                    elif radio1 == 'Excel file':
                        tmp_download_link = CDC_funcs.download_link_excel(frame, 
                                                                          'PVD_data_processed.xlsx', 
                                                                          'Click here to download excel file!')
                    st.markdown(tmp_download_link, unsafe_allow_html=True)                  
                
                text = '''
                        
                ---
                
                '''
                st.markdown(text)
                
                PVD_funcs.show_preview(frame)
                
                text = '''
                        
                ---
                
                '''
                st.markdown(text)
                
                
                
                
                #dataFrameSerialization = "legacy"
                #frame["drain_timedelta"] = pd.Timedelta(0)
                #frame["drain_timedelta"].dt.seconds
                # Determine the timedelta per baseunit
                # for base_unit in frame["Base unit [-]"].unique():
                #     frame.update(
                #         (
                #             frame.loc[df["Base unit [-]"]==base_unit, "time [HHMMSS]"] - frame.loc[df["Base unit [-]"]==base_unit, "time [HHMMSS]"].shift(1)
                #         ).rename("drain_timedelta")
                #     )
                #     #print(base_unit, "completed")
                
                # # Set the starting date
                # frame["start"] = frame["time [HHMMSS]"] - frame.drain_timedelta
                
                #st.code(frame)
                #st.write(frame)
                
                
                # if radio2 == 'Yes':
                #     cs = st.slider('Cross_section', 
                #                    min_value=wp_frame['Y [m]'].min(),
                #                    max_value=wp_frame['Y [m]'].max())
                #     st.write(cs)
                #     PVD_funcs.show_wp(wp_frame, cs)
                #PVD_funcs.show_preview_altair(frame) 
                #PVD_funcs.show_preview_bokeh(frame)
                
                #st.success('Done!')
                
if __name__ == "__main__":
    main()
    
## Export to a .csv file per pass ##
#Passes = list(set(frame.Level))
#for i in Passes:
#    pass_frame = frame[frame.Level == i]
#    pass_name = allFiles[0]
#    pass_name = pass_name.split('_')
#    pass_name = pass_name[0] + '_' + i
#    pass_frame.to_excel(f'{pass_name}.xlsx')
