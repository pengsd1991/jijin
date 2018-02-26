# -*- encoding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import sys
import random
import json

TARGET_URL = 'http://fund.eastmoney.com/data/fundranking.html'
PAGE = 74#总页数

#点击下一页
def clickNext(driver):
    while True:
        try:
            time.sleep(1)
            buttons = driver.find_element_by_xpath('//*[@id="pagebar"]').find_elements_by_tag_name('label')
            for button in buttons:
                if button.text == '下一页':
                    #此处需要用到js，否则可能保找不到元素错误
                    driver.execute_script("arguments[0].scrollIntoView(true);",button)
                    button.click()
                    print ('点击下一页成功')
                    break
            break
        except Exception as e:  
            print ('点击下一页失败，等待2s')
            time.sleep(2)
            pass
    return True

#点击基金详情
def clickTarget(driver,item):
    time.sleep(1.5)
    while True:
        try:
            button = driver.find_element_by_xpath('//*[@id="dbtable"]/tbody/tr['+str(item)+']/td[4]/a')
            driver.execute_script("arguments[0].click();",button)
            targetText = button.text
            targetHref = button.get_attribute('href')
            # button.click()
            print ('第'+str(item)+'项,找到：' + targetText+'链接：'+targetHref)
            return {'name':targetText,'url':targetHref}
            break
        except Exception as e:
            print (e)
            print ('第'+str(item)+'项打不开,睡眠1.5s')
            time.sleep(1.5)
            pass

#获取基金股票持仓数据
def getTargetVal(driver):
    index = 1
    while True:
        try:
            table = driver.find_element_by_xpath('//*[@id="position_shares"]/div[1]/table')
            table_rows = table.find_elements_by_tag_name('tr')
            break
        except :
            print ('未找到持股数据'+str(index)+'次,睡眠1s')
            if index > 9:
                print ('未找到持股数据'+str(index)+'次,出现异常！')
                return False
                break
            time.sleep(2)
            index = index + 1

    try:
        rows = len(table_rows)
        print ('共'+ str(rows-1) +'项')
        print ('--------------------------------')
        listTable = []
        for i in range(1,rows):
            listRow = []
            table_cols = table_rows[i].find_elements_by_tag_name('td')
            gupiaoName = table_cols[0].find_element_by_tag_name('a').text
            listRow.append(gupiaoName)
            gupiaoHref = table_cols[0].find_element_by_tag_name('a').get_attribute('href')
            listRow.append(gupiaoHref)
            gupiaoPrent = table_cols[1].text
            listRow.append(gupiaoPrent)
            listTable.append(listRow)
        return listTable
    except :
        print ('  未找到持股数据，---------')
        return []


if __name__ == "__main__":

    driver = webdriver.Chrome()
    driver.get(TARGET_URL)
    res = []
    for num in range(1,PAGE+1):
        dataTableTr = driver.find_element_by_xpath('//*[@id="dbtable"]').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        rows = len(dataTableTr)
        print ('********************************************')
        print ('第' + str(num) + '页,共' + str(rows) + '行')
        for item in range(1,rows+1):
            dictData = clickTarget(driver,item)
            time.sleep(1.5)
            windows = driver.window_handles
            driver.switch_to.window(windows[-1])
            itemData = getTargetVal(driver)
            dictData['value'] = itemData
            res.append(dictData)
            driver.close() #关闭新窗口
            driver.switch_to_window(windows[0]) #切换回主要
            time.sleep(random.randint(1, 3))
            print ('********************************************')
            json_str = json.dumps(res)
            file=open('data.txt','w',encoding="utf-8")  
            file.write(str(json_str));#保险起见，每次数据都重新写入文本
            file.close()
        clickNext(driver)#点击下一页
    json_str = json.dumps(res)
    file=open('data.txt','w',encoding="utf-8")  
    file.write(str(json_str));  
    file.close()  
