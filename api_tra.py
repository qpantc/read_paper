# -*- coding: utf-8 -*-
from tencentcloud.common import credential #pip install tencentcloud-sdk-python
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models
import json
import os
import re

from config import free_list, cost_list


def api_traselate(comment):
    for each in free_list: #会逐个运行api列表中的密钥，只要能成功翻译，就返回翻译的结果并跳出循环
        try:
            print(each)
            if each in cost_list:
                print('告急，正在使用付费API!\n告急，正在使用付费API!\n告急，正在使用付费API!\n')
            cred = credential.Credential(each[0], each[1])
            httpProfile = HttpProfile()
            httpProfile.endpoint = "tmt.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = tmt_client.TmtClient(cred, "ap-beijing", clientProfile)

            req = models.TextTranslateRequest()
            params_ = {}
            params = json.dumps(params_, ensure_ascii=False)
            req.from_json_string(params)
            resp = client.TextTranslate(req)
            result = json.loads(resp.to_json_string())
            print('翻译成功', result['TargetText'])
            return result # 此处运行后跳出循环
        except TencentCloudSDKException as err:
            print(err)
            if err.code == 'FailedOperation.NoFreeAmount':
                print('是额度用完的密钥，删除！')
                free_list.remove(each)


#只有题目和摘要两列的制表符文件，注意题目在前，摘要在后

#文件输出位置
outputdir = r"./outputdir"
middir = r"./middir"
rawdir = r"./rawdir"
"""
    过滤文中的隐藏文件，建立待分析的文件的文件名称
"""


def listdir_nohidden(path):
    list = []
    for f in os.listdir(path):
        if not f.startswith('.'):
            list.append(f)
    return list


""""
    保存文件方法，根据分析的文件保存数据，传入保存的文件以及保存内容进行保存
"""


def save_result(target_file, result):
    save_result_c = open(target_file, 'a', encoding='utf-8')
    for each in result:
        save_result_c.write(str(each))
        save_result_c.write('\t')
    save_result_c.write('\n')
    save_result_c.close()


"""
使用多种方法确保文件能正常打开
"""


def open_file(file):
    try:
        f = open(file, 'r', encoding='gbk')
        file_content = f.readlines()
    except:
        try:
            f = open(file, 'r', encoding='utf-8')
            file_content = f.readlines()
        except:
            try:
                f = open(file, 'r', encoding=('ascii'))
                file_content = f.readlines()
            except:
                f = open(file, 'r', encoding=('gb18030'))
                file_content = f.readlines()
    return file_content


"""
对rawdir文件夹中的文件进行预处理，并保存至middir（dir）中
"""


def pre_get_tiab(type):
    list = listdir_nohidden(rawdir)
    # 遍历文件夹中的每一个文件名
    for i in range(0, len(list)):
        path = os.path.join(rawdir, list[i])
        # 对于是文件的文件名
        if os.path.isfile(path):
            file_name = str(list[i].split(".")[0])
            file_name_path = file_name + "_tiab" + ".txt"
            file_content = open_file(path)
            target_file = os.path.join(middir, file_name_path)
            c = open(target_file, 'w', encoding='utf-8')
            c.close()
            n = 0
            for each in file_content:
                print(file_name, '文件预处理进度：', n / len(file_content))
                n += 1
                ti_ab = each.split('\t')
                if type == 'hexin':
                    TI, AB, AU, PB, DT, PY, DOI, KW, Email, Volume, Usage180 = ti_ab[
                        8], ti_ab[21], ti_ab[1], ti_ab[9], ti_ab[13], ti_ab[
                            44], ti_ab[54], ti_ab[20], ti_ab[24], ti_ab[
                                45], ti_ab[33]
                elif type == 'quanbu':
                    TI, AB, AU, PB, DT, PY, DOI, KW, Email, Volume, Usage180 = ti_ab[
                        9], ti_ab[34], ti_ab[1], ti_ab[17], ti_ab[33], ti_ab[
                            54], 0, 0, 0, 0, 0
                else:
                    TI, AB, AU, PB, DT, PY, DOI, KW, Email, Volume, Usage180 = ti_ab[
                        8], ti_ab[21], ti_ab[1], ti_ab[9], ti_ab[44], ti_ab[
                            54], 0, 0, 0, 0, 0
                result = [
                    TI, AB, AU, PB, DT, PY, DOI, KW, Email, Volume, Usage180
                ]
                save_result(target_file, result)


# 进行词频统计
def count_keyword_en(content, file_name, lang):
    txt = str(content)
    words = re.split('；|; |\n', txt)
    counts = {}
    # 对词列表中的每个词进行统计
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    # 将字典中的元素改为元组，并转化为列表
    items = list(counts.items())
    items.sort(key=lambda x: x[1], reverse=True)
    # 文件写入
    file_name_path = file_name + "_count_" + lang + ".txt"
    target_file = os.path.join(outputdir, file_name_path)
    save_result_c = open(target_file, 'w', encoding='utf-8')
    for each in items:
        word, count = each
        save_result_c.write(str(word))
        save_result_c.write('\t')
        save_result_c.write(str(count))
        save_result_c.write('\t')
        save_result_c.write('\n')
    save_result_c.close()


"""
对middir（dir）中的文件进行翻译
"""


def tra_and_save(file_content, file_name):
    file_name_path = file_name + "_tra" + ".txt"
    target_file = os.path.join(outputdir, file_name_path)
    a = open(target_file, 'w', encoding='utf-8')
    a.close()
    keywords_en = ''
    keywords_cn = ''
    i = 1
    for each in file_content:
        print(i)
        i += 1
        # time.sleep(0.2)
        ti_ab = each.split('\t')
        ti = ti_ab[0]
        try:
            ti_re = api_traselate(ti)['TargetText']
        except:
            ti_re = '我尽力了—_—!'
        # print(ti,'\n',ab)
        # 进行翻译
        # print(ti_re)
        ab = ti_ab[1]
        try:
            ab_re = api_traselate(ab)['TargetText']
        except:
            ab_re = '我尽力了—_—!!!'
        kw = ti_ab[7]
        keywords_en = keywords_en + kw
        try:
            kw_re = api_traselate(kw)['TargetText']
        except:
            kw_re = '我尽力了—_—!!!'
        keywords_cn = keywords_cn + kw_re
        # print(ab_re)
        # 写入文件
        KW = ti_ab[7]
        AU = ti_ab[2]
        PB = ti_ab[3]
        DT = ti_ab[4]
        PY = ti_ab[5]
        Volume = ti_ab[9]
        Usage180 = ti_ab[10]
        Email = ti_ab[8]
        DOI = ti_ab[6]
        result = [
            ti, ab, ti_re, ab_re, KW, AU, PB, DT, PY, Volume, Usage180, Email,
            DOI, kw_re
        ]
        save_result(target_file, result)
    count_keyword_en(keywords_cn, file_name, 'cn')
    count_keyword_en(keywords_en, file_name, 'en')


def del_file(path_data):
    try:
        for i in os.listdir(
                path_data): # os.listdir(path_data)#返回一个列表，里面是当前目录下面的所有东西的相对路径
            file_data = os.path.join(path_data, i) #当前文件夹的下面的所有东西的绝对路径
            if os.path.isfile(
                    file_data
            ) == True: #os.path.isfile判断是否为文件,如果是文件,就删除.如果是文件夹.递归给del_file.
                os.remove(file_data)
            else:
                del_file(file_data)
    except:
        print("清理干净！")


"""
将翻译后的文件保存至outputdir中
"""


def main():
    list = listdir_nohidden(middir)
    # 遍历文件夹中的每一个文件名
    for i in range(0, len(list)):
        path = os.path.join(middir, list[i])
        # 对于是文件的文件名
        if os.path.isfile(path):
            file_name = str(list[i].split(".")[0])
            # 根据分析的文件建立分析结果保存文件，并写入表头
            file_content = open_file(path)
            tra_and_save(file_content, file_name)


if __name__ == '__main__':
    pre_get_tiab('hexin') #对下载下来的文件进行预处理
    main() #执行翻译操作
    #删除中间文件和起始文件
    del_file(middir)
    #del_file(rawdir)
