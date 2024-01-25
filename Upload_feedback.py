
# Import the necessary Python libraries
import pandas as pd
import os
import time
import json
import re
import streamlit as st
from pandasql import sqldf
import openai
from Insight import insight
from Insight_df_summary import insight_df_summary


def remove_keys_from_dict(my_dict):
    key_list = ["order_no", "email_category", "silhouette", "silhouette_segment", "proportion_or_fit", "proportion_or_fit_segment", "detail", "detail_segment", "customer_sentiment_for_the_color_of_the_product", "comment_on_color_of_the_product", "print_or_pattern", "print_or_pattern_segment",
                "fabric", "fabric_segment", "brand", "appareal_category", "apparel_season", "apparel_ocassion", "apparel_target_audience", "Delayed", "Delayed_segment", "Damaged", "Damaged_segment", "Additional_charges", "Additional_charges_segment", "payment_failure", "payment_failure_segment"]

    l = [key for key in my_dict.keys() if key not in key_list]
    for i in l:
        my_dict.pop(i)
    return my_dict


def analyze(subject, text, max_tokens=1024, stop=None):
    """
    Input: Takes all reviews from the dataframe
    process: pass each review to gpt model and ask to get the fashion attributes of the review in Json format
    output: Attributes present in each review and count of attributes
    """
    print(f"subject^^^^^^^^^^^^^^{subject}")
    print(f"text^^^^^^^^^^^^^^^^^^^^^^^{text}")
    messages = [
        {"role": "system",
         "content": '''
        You are a helpful AI assistant tasked with handling customer emails related to products purchased from 'Poshmark' and categorizing them based on the 'email_category'.
        The "email_category" should fall only under one of the following categories: ['Product_quality', 'Feedback', 'Inquiry', 'Delivery', 'Payment'].
        **Payment Category:**
        * If the 'email_category' is 'Payment':
            * Extract the following attributes and their segments:
                * 'Additional_charges'
                * 'Additional_charges_segment'
                * 'payment_failure'
                * 'payment_failure_segment'
            * Analyze the sentiment of each attribute's segment:
                * Positive segment: score 1
                * Negative segment: score -1
        **Remaining Categories:**
        * Else if, the 'email_category' is among ['Product_quality', 'Delivery', 'Feedback', 'Inquiry']:
            * Identify and classify the sentiment expressed towards the relevant product attributes (if any).
            * Extract the following attributes and their segments:
                'silhouette', 'proportion/fit', 'detail', 'customer_feedback_on_color_quality', 'print/pattern', 'fabric'
            * Score sentiment for each attribute:
                * Positive segment: 1
                * Negative segment: -1
                * Neutral segment: 0
            * Handle no sentiment cases:
                * Attribute mentioned without context (name only):
                    * attribute: "NA"
                    * attribute_segment: "NA"
                * Attribute mentioned with context but no sentiment:
                    * attribute: Identified attribute name
                    * attribute_segment: "NA"
                    * sentiment: 0

            **Delivery Attribute:**
            * If the 'email_category' is 'Delivery':
                * Additionally, include the listed attributes and their segments:
                    * 'Delivery_Delayed'
                    * 'Delivery_Delayed_segment'
                    * 'Damaged_Delivery'
                    * 'Damaged_Delivery_segment'

            **Additional Attribute Inclusion for Inquiries and Feedback:**
            * If the 'email_category' is ['Inquiry', 'Feedback']:
                * Additionally, include the listed attributes and their segments:
                    * 'Additional_charges'
                    * 'Additional_charges_segment'
                    * 'payment_failure'
                    * 'payment_failure_segment'

        **Output Format:**
        * The answers should be in JSON format.

        **Note:**
        * Focus only on the listed attributes, disregard any attributes not mentioned above.
        '''},
        {"role": "user",
         "content":'''Email: [Subject: "Delivery Update Needed", Body : "Dear Support Team, I am eagerly waiting for my order (Order #76539). Its a Nike Men's Align polo T-Shirt, earlier the fitting was loose, it had a steardy pockets and overall a good build although it appears to be used and after washing it its Ocean blue color faded, hence I placed a replacement order and would like to know the reason behind the delayed delivery date. Can you please provide me with an update on when I can expect to receive my package? Thank you." ]'''},
        {"role": "assistant",
         "content":"""{"order_no" : "#76539", "email_category":"Delivery", "Delivery_Delayed" : "-1", "Delivery_Delayed_segment" : "I placed a replacement order and would like to know the reason behind the delayed delivery date", 
         "Damaged_Delivery":"-1" , "Damaged_Delivery_segment" :"and it appears to be used",
         "silhouette":"NA", "silhouette_segment" : "NA",
         "proportion_or_fit":"1","proportion_or_fit_segment":"i liked the shape and overall fit ",
         "detail":"1","detail_segment":" had a steardy pockets and overall a good build",
         "customer_sentiment_for_the_color_of_the_product":"-1", "its Ocean blue color faded after washing",
         "print_or_pattern":"NA","print_or_pattern_segment":"NA", 
         "fabric":"1", "fabric_segment": "it was very comfortable to wear"}"""},
         {"role": "user",
         "content":'''Email: [subject: "Product Quality Concern", Body: "Dear Support, I hope this message finds you well. I'm reaching out to address concerns regarding the quality of the leather jacket I recently received. Althought i liked the shape and overall fit (Order #23456), Unfortunately, the jacket exhibits noticeable scratches and defects. Also the material used are of mediocre quality which is not up to the high-quality standards I expected. As an everyday accessory, it should be free from such imperfections. Also the color seems little greyish whereas i had ordered black. I kindly request your prompt attention to this matter for a swift resolution. Thank you for your understanding." ]'''},
        {"role": "assistant",
        "content":"""{"order_no" : "#23456", "email_category":"Product_quality", "silhouette":"1", "silhouette_segment" : "Althought i liked the shape",
         "proportion_or_fit":"1","proportion_or_fit_segment":"Althought i liked the shape and overall fit ",
         "detail":"-1","detail_segment":"visible scratches and defects",
         "customer_sentiment_for_the_color_of_the_product":"-1", "comment_on_color_of_the_product":"color seems little greyish whereas i had ordered black",
         "print_or_pattern":"NA","print_or_pattern_segment":"NA", 
         "fabric":"0", "fabric_segment": "the material used are of mediocre quality which is not up to the high-quality standards"}"""},
         {"role": "user",
         "content":'''Email: [subject: "Refund Query", Body: "Hello Customer Support, I'm writing to inquire about the status of the refund process for the kurti I recently returned from order #69102. Its a women Cream and Green Floral Printed Pure Cotton Mandarin neck A-line fitted Kurti. The print was not so appealing and the length of the kurti was longer than i expected so i had placed a return request and now I'm keen to understand the expected timeline for the refund. Any information or clarity you could give me regarding the current situation would be greatly appreciated. I'm eager to hear from you and appreciate all that you've done to help us resolve this. Best regards, Joanna." ]'''},
        {"role": "assistant",
        "content":"""{"order_no" : "#69102", "email_category":"Inquiry", "silhouette":"NA", "silhouette_segment" : "NA",
         "proportion_or_fit":"0","proportion_or_fit_segment":"length of the kurti was longer than i expected",
         "detail":"NA","detail_segment":"NA",
         "customer_sentiment_for_the_color_of_the_product":"NA", "comment_on_color_of_the_product":"NA",
         "print_or_pattern":"-1","print_or_pattern_segment":"the print was not so appealing", 
         "fabric":"NA", "fabric_segment": "NA",
         "Delivery_Delayed" : "NA", "Delivery_Delayed_segment" : "NA", "Damaged_Delivery":"NA" , "Damaged_Delivery_segment" :"NA",
         "Additional_charges" : "NA", "Additional_charges_segment": "NA", 
         "payment_failure": "NA", "payment_failure_segment" :"NA"}"""},
        {"role": "user",
         "content":'''Email: [subject: "Amount has been debited", Body: "Hello support team, Hope you are doing well! I was trying to place an order for a hooded sweatshirt, however it seems my debit card has been charged twice for the same transaction but the payment is showing as failed. I have checked my bank statements, the amount is still not credited. Additionally, my most recent order was delivered in the morning, but even though I had already made a prepaid payment, I was charged extra for it. Please help me as soon as possible. Thanks, [Customer Name] " ]'''},
        {"role": "assistant",
        "content":"""{"order_no" : "NA", "email_category":"Payment", 
        "Additional_charges" : "-1", "Additional_charges_segment": "already made a prepaid payment, I was charged extra for it", 
        "payment_failure": "-1", "payment_failure_segment" : "debit card has been charged twice for the same transaction but the payment is showing as failed, amount is still not credited"}"""},
        {"role": "user",
         "content": "Email: [Subject:" + subject + "," + "Mail_body : " + text+"]"}  # text =  mail body
    ]

    response = openai.ChatCompletion.create(
        engine="chatgpt",  # 'fnf-gpt',
        messages=messages,
        max_tokens=max_tokens,
        stop=stop,
    )

    result = response["choices"][0]["message"]["content"]
    # print("\n\n"+result)
    try:
        result = re.search(
            r'\{([^}]+)\}', result).group().replace('" ,"', '","').replace(', ,', ',')
        # print(result)
        final_df = json.loads(result)
        final_df = remove_keys_from_dict(final_df)
        # print(final_df)
        new_ent = {"subject": subject.replace(",", " "), "message": text.replace(",", " ")}
        new_ent.update(final_df)
        # final_df["message"] = "test"
        # final_df["subject"] = "subject"
        # print(type(new_ent))
        print(new_ent)

        return new_ent
    except Exception as e:
        print(e)
        print("\n\n", result)
        return 0


def insert_json_into_csv(json_data, excel_file):
    try:
        existing_df = pd.read_csv(excel_file)
    except Exception as e:
        print("pre processing Json data : ", json_data)
        existing_df = pd.DataFrame([json_data])

    # "Delayed", "Delayed_segment", "Damaged", "Damaged_segment", "Additional_charges", "Additional_charges_segment", "payment_failure", "payment_failure_segment"
     # .reset_index(drop=True)
    new_dict = {i: None for i in ["Delayed", "Delayed_segment", "Damaged", "Damaged_segment",
                                  "Additional_charges", "Additional_charges_segment", "payment_failure", "payment_failure_segment"]}
    # Merge the new key-value pairs into the original dictionary
    for key, value in new_dict.items():
        try:
            if key not in json_data:
                json_data[key] = value
        except Exception as e:
            print(key)
    print("post processed Json data : ", json_data)
    json_df = pd.DataFrame([json_data])
    # Insert the JSON data into the existing DataFrame at the specified row index
    existing_df = existing_df.append(json_df, ignore_index=True)
    # print(existing_df)
    # Concatenate the new DataFrame with the existing one, and reset the index
    # Write the updated DataFrame back to the Excel file
    # existing_df.to_csv(xl_file, index=False)
    existing_df.to_csv(excel_file, index=False)
    # return excel_file
    print(
        f"Excel file generated with name --------------------------------{excel_file}")


def generate_gpt_prediction(subject, text, max_tokens=1024, stop=None):
    """
    Input: Takes all reviews from the dataframe
    process: pass each review to gpt model and ask to get the fashion attributes of the review in Json format
    output: Attributes present in each review and count of attributes
    """
    # print(text)
    messages = [
        {"role": "system",
         "content": '''
        You are an AI assistant designed to analyze customer emails related to purchases from 'Poshmark' and extract specific metadata from the email content. The metadata to be extracted includes: "apparel_category," "apparel_target_audience," "brand," "apparel_season," and "apparel_occasion."
        Response Generation Rules:
        1. "apparel_category" can be any clothing items.
        2. The "apparel_occasion" can be categorized into options like ['beach', 'casual', 'office wear', 'sport', 'Global & traditional wear', 'party'].
        3. The "apparel_season" may fall under the categories: ['summer', 'winter', 'N/A'].
        4. For "apparel_target_audience," consider options like ['Women', 'Men', 'Kids'].
        5. Extract the specified features, whichever is mentioned in the customer's email : ["apparel_category," "apparel_target_audience," "brand," "apparel_season," "apparel_occasion"]; for example, considering customer is talking about a GAP sweatshirt purchased for winter casual wear so extracted features would be :['Sweatshirt', 'NA', 'GAP', 'winter', 'casual']
        6. Generate the output is JSON format.
        '''},
        {"role": "user",
         "content": '''Email: [Subject: Delivery Update Needed, Mail_body : Dear Support Team, I am eagerly waiting for my order (Order #76539). Its a Silver Party wear dress earlier the fitting was loose but I liked the tshirt, as it was very comfortable to wear and its Ocean blue color didnt fade after washing hence I placed a replacement order and would like to know the estimated delivery date. Can you please provide me with an update on when I can expect to receive my package? Thank you. ]'''},
        {"role": "assistant",
         "content": """[{"appareal_category": "Dress", "apparel_target_audience" : "Women", "brand":"NA",
         "apparel_season" : "NA","apparel_ocassion": "Party"}]"""},
        {"role": "user",
         "content": "Email: [Subject:" + subject + "," + "Mail_body : " + text+"]"}  # text = subject + email
    ]

    response = openai.ChatCompletion.create(
        engine="chatgpt",  # 'fnf-gpt',
        messages=messages,
        max_tokens=max_tokens,
        stop=stop,
    )

    result = response["choices"][0]["message"]["content"]
    # print(type(result))
    try:
        result = re.search(
            r'\{([^}]+)\}', result).group().replace('" ,"', '","').replace(', ,', ',')
        # print(result)
        final_df = json.loads(result)
        return final_df
    except Exception as e:
        print(e)
        print("\n\n", result)
        return None


def iter(org_xl_file, excel_file):
    try:
        data = pd.read_csv(org_xl_file)
    except Exception:
        data = pd.read_excel(org_xl_file)

        # Write the DataFrame to a CSV file
        data.to_csv(org_xl_file.split(".")[0]+".csv", index=False)
        data = pd.read_csv(org_xl_file.split(".")[0]+".csv")
    c = 0

    for row in data[:].itertuples():
        # if c<3:
        # print(row.Subject, row.Message)
        # print(type(row.Subject))
        df_1 = generate_gpt_prediction(row.Subject, row.Message)
        df = analyze(row.Subject, row.Message)
        for key in df:
            try:
                df[key] = int(df[key])
            
            except Exception as e:
                if e is not ValueError:
                    print(e)
        if df_1 is not None:
            try:
                df.update(df_1)
            except AttributeError as e:
                print(e)
        # print(df)
        # insert_json_into_csv(df, xl_file)
        insert_json_into_csv(df, excel_file)
        # print(df)
        c += 1
        print(c)
        time.sleep(3)


def upload_feedback():
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
        "Upload Files", accept_multiple_files=False, type=['csv', 'xlsx'])

    if uploaded_files:
        excel_file = uploaded_files.name
        excel_file = excel_file.replace('.csv', '_converted.csv')
        iter(uploaded_files.name, excel_file)
        # read the uploaded csv files as a dataframe
        df = pd.read_csv(excel_file, encoding_errors='ignore')
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
        # if len(df)<5:
        sample_df = df.sample(4, ignore_index=True)
        # else:
        #     sample_df = df.sample(10, ignore_index=True)
            
        sample_df.iloc[:,1] = sample_df.iloc[:,1].str.replace(',', ' ') #.apply(axis = 1).replace(",", " ")
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
                        """If the question is not relevant to the table provided give output as "Irrelenat question". Give output in the form of dictionary where key will be name of the insight and value will be <sql query to run using pandasql module of python>. Following is a sample from actual dataset, Notice certain columns such as "Fabric", "print_or_pattern" have values such as (-1,0,1), where 1 denotes a positive sentiment, -1 for a negative sentiment and 0 for a neutral sentiment, for your reference. : \n""" + \
                        sample_df.to_csv(index=False)
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
