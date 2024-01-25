
import ast
import openai
import streamlit as st


def insight(pre_prompt_gpt):
    """
    This function is called from main function to get the sql query.
    Generates the sql query to get releveant data with respect to question.

    Args:
        pre_prompt_gpt (string): prompt for GPT model.

    Returns:
        dict: The dictionary containing title of insight as key and sql query as values
    """
    # add instruction in the prompt
    prompt = pre_prompt_gpt+"""output example
       if question is relevant to the table then output:
       {'insight_name':'''sql query'''}
       if question is not relevant to the table then output:
       "1.No data found
        2.Irrelevant question"

        """
    # Generate sql query using the OpenAI GPT-4 model.
    completion = openai.ChatCompletion.create(
        engine="gpt4-8k",
        temperature=0,
        messages=[{'role': 'system', 'content': 'You are a business analytics insight generater'},
                  {"role": "user", "content": prompt}])
    # Retrieve the generated sql query from the response.
    output = completion["choices"][0]["message"]['content']
    print(
        '#####################insight_output####################################')
    print(output)
    # st.text(completion)
    # Check if the generated output contains a JSON-like dictionary structure.
    if output.find('{') != -1:
        # Extract the dictionary structure from the output.
        output_dict_str = output[output.find('{'):output.rfind('}')+1]
        # Parse the dictionary string into a Python dictionary.
        output_dic = ast.literal_eval(output_dict_str)
        # Return the parsed dictionary as the result.
        return output_dic
    else:
        # If the output is not in a dictionary format, display it as a Markdown message.
        st.markdown(f"### **{output}**", unsafe_allow_html=True)
        return {}
