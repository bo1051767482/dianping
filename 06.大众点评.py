import re
import requests
from lxml import etree
import json
from fake_useragent import UserAgent

ua = UserAgent()

#得到css样式
url = 'http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/shoptextcss/textcss.hHGEFeGyJG.css'
response = requests.get(url=url)

#一、找到每个类名标识
pattern = re.compile(r'.fa-.*?}')
addr_items = pattern.findall(response.text)

pattern = re.compile(r'.fr-.*?}')
review_items = pattern.findall(response.text)

#二、找到对应的汉字表(address,review)
pattern = re.compile(r'//.*?.svg')
file_svg = pattern.findall(response.text)
print(file_svg)

#网络请求函数
def get_content(url):
    response = requests.get(url=url)
    return response.text

#地址编码表和#评论编码表
address_svg_url = 'http:'+file_svg[0]
review_svg_url = 'http:'+file_svg[1]
address_str = get_content(address_svg_url)
review_str = get_content(review_svg_url)

#由于拿到的是带格式的内容，所以需要提取一下数据
line_pattern = re.compile(r'class="textStyle">(.*?)</text>')
#(1)地址
add_lines = line_pattern.findall(address_str)
address_content =''
for line in add_lines:
    address_content+=line
    # 保存
    with open('address_svg.txt', 'a', encoding='utf-8') as fp:
        fp.write(line)

# (2)review
review_lines = line_pattern.findall(review_str)
review_content =''
for line in review_lines:
    review_content += line
    # 保存
    with open('review_svg.txt', 'a', encoding='utf-8') as fp:
        fp.write(line)


#三、生成标识和汉字编码表的对照关系
word_dic = {}
#（1）地址
addr_items.pop()#最后一个标识不合法，去掉
for item in addr_items:

    #字宽14，高7
    # 拿位置
    locaton_x = re.compile('background:(.*?)px')
    x_list = locaton_x.findall(item)

    locaton_y = re.compile('px (.*?)px')
    y_list = locaton_y.findall(item)

    x = abs(float(x_list[0]))
    y = abs(float(y_list[0]))

    # print(item[:8],'loc:',x,y)
    #行、列变为一行读取
    #         x   y  index
    # 第一行：0   7    0
    # 第二行：0   37   42
    x_0 = int(x/14)#表示第几列
    y_0 = int(y)//30#表示第几行
    # print('index:',x_0,y_0)
    #                 行  行中第n个字
    word = add_lines[y_0][x_0:x_0+1]
    print(item[:8], word)

    #添加到字典当中
    k = item[1:8]
    word_dic[k]=word

data = json.dumps(word_dic,ensure_ascii=False)
with open('word_list.txt','w',encoding='utf-8') as fp:
    fp.write(data)

#（2）评论
review_items.pop()#最后一个标识不合法，去掉
for item in review_items:

    #字宽14，高7
    # 拿位置
    locaton_x = re.compile('background:(.*?)px')
    x_list = locaton_x.findall(item)

    locaton_y = re.compile('px (.*?)px')
    y_list = locaton_y.findall(item)

    x = abs(float(x_list[0]))
    y = abs(float(y_list[0]))

    # print(item[:8],'loc:',x,y)
    #行、列变为一行读取
    #         x   y  index
    # 第一行：0   7    0
    # 第二行：0   37   42
    x_0 = int(x/14)#表示第几列
    y_0 = int(y)//30#表示第几行
    # print('index:',x_0,y_0)
    #                 行  行中第n个字
    word = review_lines[y_0][x_0:x_0+1]
    print(item[:8], word)

    #添加到列表当中
    k = item[1:8]
    word_dic[k]=word



#四、替换页面内容

with open('dianping.html','r',encoding='utf-8') as fp:
    content = fp.read()
# print(content)

pattern = re.compile(r'<p class="desc">([\d\D].*?)</p>')
span_desc_list = pattern.findall(content)
for desc in span_desc_list:

    #old
    pattern = re.compile(r'<span class="fr-.*?"></span>')
    span_list = pattern.findall(content)

    #new
    pattern = re.compile(r'<span class="(fr-.*?)"></span>')
    fr_list = pattern.findall(content)

    print(span_list)
    print(fr_list)
    i = 0
    while i<len(span_list):

        k = fr_list[i]
        new_value = word_dic[k]
        old_value = span_list[i]

        desc.replace(old_value,new_value)
        # # print(str)
        #
        #
        # print(span_list[i],'---value:',new_value)
        # str = desc
        # # print(str)
        # str.replace(old_value,new_value)
        # # print(str)
        i+=1

    # print(desc)
    # break





def aa():
    url = 'http://www.dianping.com/shop/3500059'
    headers = {
        'If-Modified-Since': 'Thu, 02 Aug 2018 00:20:50 GMT',
        'If-None-Match': 'ce08cfcf270df83dbedbc9d835ec8669',
        'User-Agent':ua.random,
        'Cookie': 'cy=4; cye=guangzhou; _lxsdk_cuid=164ef6ddb43c8-0d6922d8688559-6114147a-fa000-164ef6ddb44c8; _lxsdk=164ef6ddb43c8-0d6922d8688559-6114147a-fa000-164ef6ddb44c8; _hc.v=68578c06-13d2-8a81-6102-8891acaea578.1533025312; s_ViewType=10; ua=dpuser_22848850644; ctu=4e978e568e6e9ade75538846c643a64ee8aa3c4fdb6622094760399b30f2b0b2; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; thirdtoken=6A94EEDD9D83195355E54B28D35D9C04; dper=523ee0c18bda72e1ecf3a7bbd73f8f10b3cc8956115b9d35f24c5958c4fb0f1867b9c701d0f13ec2a2213564e7fe135cea4b782aac85c1640ece59e9f625c172eaba0ba2899597ff357262d2f91b5bf6eddae1c1c485df04078a8a2543aa9d70; ll=7fd06e815b796be3df069dec7836c3df; ctu=56286ee3bef4ebf7aa06d8188f48f6e2439852afac1fc0f929edbdf19d74e54ec43bde5237c1ec81f735c6fac63a9381; JSESSIONID=C7F7C1C45A0FC69720DAE0A2032B7D92; _lxsdk_s=164fa7ed6fe-45b-b5-4f8%7C%7C58'
    }
    response = requests.get(url=url,headers=headers)

    from selenium import webdriver
    import time

    driver = webdriver.PhantomJS(executable_path=r'D:\phantomjs-2.1.1-windows\bin\phantomjs.exe')
    driver.get(url=url)


    with open('dianping01.html','w',encoding='utf-8') as fp:
        fp.write(driver.page_source)

    content = driver.page_source
    pattern = re.compile(r'<span class="fr-.*?"></span>')
    span_list = pattern.findall(content)
    for span in span_list:
        print(span)
    # content.replace(span,)






