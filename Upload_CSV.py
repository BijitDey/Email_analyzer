
# Import the necessary Python libraries
import pandas as pd
import os
import streamlit as st
from pandasql import sqldf
import openai
from Insight import insight
from Insight_df_summary import insight_df_summary


def Upload():
    """
    Allows user to upload file from the local storage.
    Internally calls insight.py and insight_df_summary.py to get sql query,
    natural language insight and python plot.
    """

    # Load credentials
    openai.api_type = os.getenv('api_type')
    openai.api_base = os.getenv('api_base')
    openai.api_version = os.getenv('api_version')
    openai.api_key = os.getenv('api_key')

    # Use the file_uploader to allow users to upload csv files
    uploaded_files = st.sidebar.file_uploader(
        "Upload Files", accept_multiple_files=False, type='csv')

    if uploaded_files:
        # read the uploaded csv files as a dataframe
        df = pd.read_csv(uploaded_files, encoding_errors='ignore')
        # get schema of dataframe
        df_col_dtype = pd.DataFrame(df.dtypes)
        # reset the schema
        df_col_dtype = df_col_dtype.reset_index()
        # rename the column of schema daraframe
        df_col_dtype.columns = ['column', 'dtype']
        # display the schema daraframe in UI sidebar
        st.sidebar.dataframe(df_col_dtype, hide_index=True)
        # store column names in list
        columns = df.columns.to_list()
        # join the columns names to string
        col_str = ', '.join(columns)
        # st.dataframe(df.sample(5), height=220)
        # store and display the random 10 sample rows of dataframe on UI(uploaded csv file)
        if len(df)<5:
            sample_df = df.sample(4, ignore_index=True)
        else:
            sample_df = df.sample(10, ignore_index=True)
        sample_df.iloc[:,1] = sample_df.iloc[:,1].str.replace(',', ' ') 
        st.dataframe(sample_df, height=220)

        # user_prompt = st.text_input(
        #     "Any instruction or comments (Optional):", key="sql_prompt")
        # user_prompt = user_prompt + " "
        user_prompt = " "
        if user_prompt:
            with st.spinner('Wait for it ...'):
                col_str += col_str+user_prompt
        # Use st.form for handling user input and form submission
        with st.form("plot_form"):
            # Create a text input box for user question
            question_prompt = st.text_input(
                "Ask Question:", key="question_prompt")
            # Use st.columns to create multiple columns for layout purposes
            col1, col2, col3 = st.columns(3)
            # Use st.form_submit_button to create a button for generating insight
            plot_submit = col1.form_submit_button(
                "Generate Insights")
            # Create a checkbox for show the code functionality
            show_code = col2.checkbox('Show the code')
            # Create a checkbox for explain the code functionality
            explain_code = col3.checkbox('Explain the code')

            if plot_submit:
                # Use st.spinner to display a loading spinner while processing
                with st.spinner('Wait for it...Generating the insight and plots...'):
                    # prompt to get sql query :instruction+column names+sample_rows
                    pre_prompt_gpt = """Give relevant insights from the dataframe df with columns """+col_str+""" based on the following question :"""+question_prompt +\
                        """If the question is not relevant to the table provided give output as "Irrelevant question". Give output in the form of dictionary where key will be name of the insight and value will be <sql query to run using pandasql module of python>. Following is a sample from actual dataset, Notice certain columns such as "fabric", "print_or_pattern" have values such as (-1,0,1) , where 1 denotes a positive sentiment, -1 for a negative sentiment and 0 for a neutral sentiment, for your reference. : \n""" + \
                        sample_df.drop(["message"], axis=1).to_csv(index=False)
                    
                    
                    # Call the helper_function insight from insight.py file to get sql query to filter the relevant data.
                    output_dic = insight(pre_prompt_gpt)
                    # output_dic will contain title of insight as key and value will be sql query to run using pandasql module of python to get relevant data based on question.
                    if output_dic:

                        print(
                            '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@DICTIONARY@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                        print(output_dic)

                        for k, v in output_dic.items():
                            print(
                                '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@VALUE@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
                            print(v)

                            # st.text(k)
                            # st.text(v)
                            # execute sql query on pandas dataframe and store filtered dataframe in insight_df
                            insight_df = sqldf(v, locals())

                            print(
                                '***********************************q_to_df***********************************')
                            print(insight_df)
                            if not insight_df.empty:

                                try:
                                    # display title of insight on UI
                                    st.markdown(
                                        f"### <u>**{(k).replace('_',' ').title()}**</u>", unsafe_allow_html=True)
                                    # Show the code
                                    if show_code:

                                        st.markdown(
                                            f"###### **{'SQL query to fetch relevant data'}**", unsafe_allow_html=True)
                                        st.code(
                                            v, language='sql')
                                    # explain the sql query
                                    if explain_code:
                                        # Create an expander to see explanation of the sql query
                                        with st.expander(f"###### **{'See code explaination'}**"):
                                            # define prompt to get code explanation
                                            prompt = """Explain the following query : """+v
                                            # use GPT to get code explanation
                                            completion = openai.ChatCompletion.create(
                                                engine="gpt4-8k",
                                                # engine="chatgpt",
                                                temperature=0,
                                                messages=[{'role': 'system', 'content': 'Your job is to explain the code '},
                                                          {"role": "user", "content": prompt}])

                                            output = completion["choices"][0]["message"]['content']
                                            # display explanation if clicked on expander
                                            st.write(output)
                                    # Call the helper_function insight_df_summary from insight_df_summary.py file to get natural language insight and python code for plot.
                                    insight_df_summary(
                                        k, insight_df, show_code, explain_code, question_prompt)
                                # handle token limit errors
                                except openai.error.InvalidRequestError as r:
                                    st.text(r)
                                    print(
                                        'Relevant data exceeded token limit')
                                    st.markdown(
                                        f"### **Relevant data exceeded token limit**", unsafe_allow_html=True)
                                except Exception as e:
                                    st.text(e)
                                    print(
                                        'Something went wrong')
                                    st.markdown(
                                        f"### **Something went wrong**", unsafe_allow_html=True)
                            else:
                                # if insight_df is empty: means no relevant data

                                st.markdown(
                                    f"### **No data available relevent to this query**", unsafe_allow_html=True)
                                print(
                                    '********************************EMPTY DATAFRAME************')
#################################################################
