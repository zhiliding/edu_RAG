import os
os.environ['CURL_CA_BUNDLE'] = ''

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from langchain_core.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_community.llms.tongyi import Tongyi
from langchain.chains import SimpleSequentialChain

template = "我的邻居姓{lastname}, 他生了个儿子, 给他儿子起个名字"

first_prompt = PromptTemplate(input_variables=["lastname"], template=template)
llm = Tongyi(model="qwen3-max")

first_chain = LLMChain(llm=llm, prompt=first_prompt)

second_prompt = PromptTemplate(input_variables=["child_name"], template="邻居的儿子名字叫{child_name},给他起个小名")

second_chain = LLMChain(llm=llm, prompt=second_prompt)

overall_chain = SimpleSequentialChain(chains=[first_chain, second_chain], verbose=True)

print(overall_chain)
print('*'*80)

try:
    catchphrase = overall_chain.invoke("王")
    print(catchphrase)
except Exception as e:
    print(f"调用失败: {e}")
    print("\n请检查:")
    print("1. 网络连接是否正常")
    print("2. 是否设置了正确的通义千问API密钥")
    print("3. 尝试运行: pip install --upgrade certifi requests urllib3 dashscope")
