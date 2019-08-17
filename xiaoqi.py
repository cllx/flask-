import json
import score
import os
import shutil
from collections import OrderedDict
import copy

#把对齐后的文件读出来
def read_file(merge_file):
	with open(merge_file, 'r') as f:
		dictionary = json.load(f)
	return dictionary

#给消歧标记重新编号
def change_flag(dictionary):
	global num #消歧标记的编号
	global number
	global disambiguate_id
	global disambiguate_flag
	for key, value in dictionary.items():
		#消歧标记都在列表下面
		if (type(value).__name__=='list'):
			flag_list = [] #每个list下的编号集合
			#把每个list下的消歧标记编号放到列表中
			for i in value:
				if disambiguate_flag in i:
					#给每个值加一个id
					i[disambiguate_id] = number
					number += 1
					#把每个list下的消歧标记编号放到列表中
					flag_list.append(i[disambiguate_flag])
			#如果是相同的消歧标记
			if len(set(flag_list)) == 1:
				for i in value:
					#把新的消歧标记设置成num
					if disambiguate_flag in i:
						i[disambiguate_flag] = num
				num += 1
			#如果有多种消歧标记
			elif len(set(flag_list)) > 1:
				#对于每一种消歧标记分别重新设置num
				for f in set(flag_list):
					for i in value:
						if disambiguate_flag in i and i[disambiguate_flag] == f:
							i[disambiguate_flag] = num
							#print(value[i][disambiguate_flag])
					num += 1
		#如果是字典就递归调用函数
		elif (type(value).__name__=='dict'):
			change_flag(value)

'''
找出有消歧标记的属性，没有消歧标记的属性标-1
'''
def add_delete_flag(dictionary):
	global disambiguate_flag
	for key, value in dictionary.items():
		#如果有消歧标记，value一定是字典
		if (type(value).__name__=='str'):
			dictionary[key]	= -1
		#有时是列表嵌套字典
		elif (type(value).__name__=='list'):
			for i in range(len(value)):
				if disambiguate_flag not in value[i]:
					value[i] = -1
		#如果是字典就递归调用函数
		else:
			add_delete_flag(value)

'''
把所有标-1的属性都删除
'''
def del_value(dictionary):
	#遍历字典的值，如果是-1就删除
	for key in list(dictionary.keys()):
		if dictionary[key] == -1:
			del(dictionary[key])
	for value in dictionary.values():
		#如果值是列表，遍历列表的拷贝，如果有-1就删除
		if (type(value).__name__=='list'):
			copy_value = value[:]
			for i in copy_value:
				if i == -1:
					value.remove(i)
		#如果值是字典就递归调用
		elif (type(value).__name__=='dict'):
			del_value(value)

'''
删除属性后会有一些属性值为空，把所有空值删除
'''
def del_empty_array(dictionary):
	#遍历字典，如果是空值就删除
	for key in list(dictionary.keys()):
		if not dictionary[key]:
			del(dictionary[key])
	#遍历值，如果是字典就递归调用
	for value in dictionary.values():
		if (type(value).__name__=='dict'):
			del_empty_array(value)

def find_same_flag(dictionary):
	global multi_values
	global headline
	global headline2
	global source
	global disambiguate_id
	global disambiguate_flag
	global xiaoqi_list
	global name
	for key, value in dictionary.items():
		#基本信息
		if key == headline['jibenxinxi']:
			#is_multi_value = 1
			#[职业，毕业院校...]
			for va in value:
				#[职业..., 职业...]
				for v in value[va]:
					num = v[disambiguate_flag]
					number = v[disambiguate_id]
					#print(number)
					#{'职业': '学者，教授', '消歧标记': 1, '来源': 'fang_hudong'}
					for k in v:
						if k != disambiguate_flag and k != source and k != disambiguate_id:
							if k in multi_values:
								is_multi_value = 1
							else:
								is_multi_value = 0
							#方滨兴 职业:学者，教授0
							#print(name + ' ' + k + ' ' + str(v[k]) + ' ' + str(num) + ' '+ 
							#	str(is_multi_value) + ' ' + str(number))
							xiaoqi_list.append(name + ' ' + k + ' ' + v[k] + '|' + str(num) + ' '+ 
								str(is_multi_value) + ' ' + str(number))
		#人物履历
		elif key == headline['renwulvli']:
			is_multi_value = 0
			#[教育经历，工作经历]
			for key1 in value:
				if key1 == headline2['jiaoyujingli']:
					#[本科，硕士，博士，博士后]
					for key2 in value[key1]:
						#[结束时间，学位...]
						for key3 in value[key1][key2]:
							#[结束时间，结束时间...]
							for key4 in value[key1][key2][key3]:
								#{'结束时间': '1981', '消歧标记': 1, '来源': 'fang_hudong,fang_360,fang_wiki'}
								for k in key4:
									num = key4[disambiguate_flag]
									number = key4[disambiguate_id]
									#print(number)
									if k != disambiguate_flag and k != source and k != disambiguate_id:
										#print(name + ' ' + key2 + k + ' ' + str(key4[k]) + ' ' + str(num) 
										#	+ ' '+ str(is_multi_value) + ' ' + str(number))
										xiaoqi_list.append(name + ' ' + key2 + k + ' ' + str(key4[k]) + '|' + 
											str(num) + ' '+ str(is_multi_value) + ' ' + str(number))
				if key1 == headline2['gongzuojingli']:
					#任职
					for key2 in value[key1]:
						#print(key2)
						value_list = [] #把多种消歧标志放到列表里
						#[所在单位，起始时间...]
						for key3 in value[key1][key2]:
							#[所在单位，起始时间]
							for key4 in key3:
								if key4 == disambiguate_flag:
									value_list.append(key3[key4])
						#print(value_list)
						for i in set(value_list):
							for key3 in value[key1][key2]:
								if key3[disambiguate_flag] == i:
									if key2 == headline2['renzhi']:
										xiaoqi_list.append(name + ' ' + key3[headline2['qishishijian']] + '-' + 
											key3[headline2['jieshushijian']] + key3[headline2['didian']] + 
											key3[headline2['suozaidanwei']] + ' ' + key3[headline2['zhiwei_zhicheng']]
											+ '|' + str(i) + ' '+ str(is_multi_value) + ' ' + str(key3[disambiguate_id]))
								
									#任免_辞职
									elif key2 == headline2['renmian_cizhi']:
										xiaoqi_list.append(name + ' ' + key3[headline2['shijiandian']] + 
											headline2['renmian_cizhi'] + ' ' + key3[headline2['renmianzhiwei_zhicheng']]
											 + '|' + str(i) + ' '+ str(is_multi_value) + ' ' + str(key3[disambiguate_id]))

		#其他职务
		elif key == headline['qitazhiwu']:
			#[学术兼职]
			for key1 in dictionary[key]:
				if key1 == headline2['xueshujianzhi'] or key1 == headline2['jishugongzuojianzhi']:
					is_multi_value = 0
					#[起始时间，结束时间...]
					for v in dictionary[key][key1]:
						num = v[disambiguate_flag]
						number = v[disambiguate_id]
						xiaoqi_list.append(name + ' ' + v[headline2['qishishijian']] + v[headline2['jieshushijian']] 
							+ v[headline2['zuzhijigou']] + ' ' + v[headline2['zhiwei_zhicheng']] + '|' + str(num) + 
							' '+ str(is_multi_value) + ' ' + str(number))
				#社会兼职
				else:
					is_multi_value = 1
					for v in dictionary[key][key1]:
						num = v[disambiguate_flag]
						number = v[disambiguate_id]
						xiaoqi_list.append(name + ' ' + v[headline2['qishishijian']] + v[headline2['jieshushijian']] 
							+ v[headline2['zuzhijigou']] + ' ' + v[headline2['zhiwei_zhicheng']] + '|' + str(num) + 
							' '+ str(is_multi_value) + ' ' + str(number))

		#科研方向
		elif key == headline['keyanfangxiang']:
			pass
		#研究领域
		elif key == headline['yanjiulingyu']:
			pass
		#主要荣誉
		elif key == headline['zhuyaorongyu']:
			is_multi_value = 1
			#[时间点，颁奖单位]
			for v in dictionary[key]:
				num = v[disambiguate_flag]
				number = v[disambiguate_id]
				#print(name + ' ' + v[headline2['shijiandian']] + v[headline2['banjiangdanwei']] + 
				#	' ' + v[headline2['shouyujiangxiangmingcheng']] + ' ' + str(number) + ' '+ str(is_multi_value))
				xiaoqi_list.append(name + ' ' + v[headline2['shijiandian']] + v[headline2['banjiangdanwei']] + 
					' ' + v[headline2['shouyujiangxiangmingcheng']] + '|' + str(num) + ' '+ str(is_multi_value)
					+ ' ' + str(number))
		#主要成果
		elif key == headline['zhuyaochengguo']:	
			is_multi_value = 1
			#[承担项目类，研究成果类...]
			for key1 in dictionary[key]:
				#if key1 == headline2['xueshulunzhulei']:
				value_list = [] #把多种消歧标志放到列表
				#[时间点，论著名称...]
				for k in dictionary[key][key1]:
					value_list.append(k[disambiguate_flag])
				for i in set(value_list):
					for k in dictionary[key][key1]:
						vv = [] #存放关键词
						for kk in k:
							if kk != disambiguate_flag and kk != disambiguate_id and kk != source:
								vv.append(k[kk])
						if k[disambiguate_flag] == i:
							#print(name + ' ' + k[headline2['shijiandian']] + ' ' + k[headline2['lunzhumingcheng']]
							#	 + ' ' + str(i) + ' '+ str(is_multi_value))
							xiaoqi_list.append(name + ' ' + vv[0] + ' ' + vv[1] + '|' + str(i) + ' '+ 
								str(is_multi_value) + ' ' + str(k[disambiguate_id]))
		#学术报告
		elif key == headline['xueshubaogao']:
			pass
		#人物评价/外界评价
		elif key == headline['renwupingjia']:
			pass
		#人物影响
		elif key == headline['renwuyingxiang']:
			pass
		#个性寄语
		elif key == headline['gexingjiyu']:
			pass
		#社会争议_争议事件
		elif key == headline['shehuizhengyi']:
			pass
		#获奖争议
		elif key == headline['huojiangzhengyi']:
			pass
		#院士名
		elif key == headline['yuanshiming']:
			pass

#把关键字写入文件
def write_keywords_to_file(xiaoqi_list):
	with open('keywords.txt', 'w', encoding = 'utf-8') as f:
		for i in xiaoqi_list:
			f.write(i)
			f.write('\n')
		print('success')

#记录需要保留的消歧编号
def record_id():
	global disambiguate_id_list
	global disambiguate
	for d in disambiguate:
		disambiguate_id_list.append(d['disambiguate_id'])
	#print(disambiguate_id_list)

#不在列表中的属性删除
def find_flag(dictionary):
	global disambiguate_id_list
	for key, value in dictionary.items():
		if (type(value).__name__=='list'):
			value_copy = value[:]
			for i in value_copy:
				#如果需要消歧，且编号不在消歧列表中，删除该元素
				if disambiguate_id in i and str(i[disambiguate_id]) not in disambiguate_id_list:
					#print(i)
					value.remove(i)
		#如果是字典就递归调用函数
		elif (type(value).__name__=='dict'):
			find_flag(value)

#删除消歧编号、消歧标记
def delete_flag(dictionary):
	global disambiguate_flag
	for key, value in dictionary.items():
		if (type(value).__name__=='list'):
			value_copy = value[:]
			for i in value_copy:
				if disambiguate_flag in i:
					del i[disambiguate_flag]
					del i[disambiguate_id]
	#如果是字典就递归调用函数
		elif (type(value).__name__=='dict'):
			delete_flag(value)

#给字典重新排序（字典是无序的）
def merge_dict(dictionary):	
	global headline
	global headline2
	global source
	monitorItems = OrderedDict()
	alist = [headline['jibenxinxi'], headline['renwulvli'], headline['qitazhiwu'], headline['keyanfangxiang'], 
		headline['yanjiulingyu'], headline['zhuyaorongyu'], headline['zhuyaochengguo'], headline['xueshubaogao'], 
		headline['renwupingjia'], headline['renwuyingxiang'], headline['gexingjiyu'], headline['shehuizhengyi'], 
		headline['huojiangzhengyi'], headline['yuanshiming'], headline2['zhongwenming'], headline2['waiwenming'], headline2['xingbie'], 
		headline2['chushengriqi'], headline2['chushengdi'], headline2['guoji'], headline2['minzu'], headline2['zhiye'], 
		headline2['biyeyuanxiao'], headline2['zhengzhimianmao'], headline2['daibiaozuopin'], headline2['zhuyaochengjiu'], 
		headline2['cengrenzhi'], headline2['xinyang'], headline2['yuanji'], headline2['jiaoyujingli'], headline2['gongzuojingli'],
		headline2['benke'], headline2['shuoshiyanjiusheng'], headline2['boshiyanjiusheng'], headline2['boshihou'],
		headline2['renzhi'], headline2['renmian_cizhi'], headline2['xueshujianzhi'], headline2['jishugongzuojianzhi'], 
		headline2['shehuijianzhi'], headline2['xueshulunzhulei'], headline2['sanwenlei'], headline2['chengdanxiangmulei'],
		headline2['yanjiuchengguolei'], headline2['famingzhuanlilei'], headline2['rencaipeiyanglei'], headline2['qishishijian'], 
		headline2['jieshushijian'], headline2['xuexiaomingcheng'], headline2['suoshuyuanximing'], headline2['xuexiaomingcheng_keyanjigou'], 
		headline2['suoshuyuanximing_ketizu'], headline2['daoshi'], headline2['xueli'], headline2['xuewei'], source]
	for key in alist:
	    if dictionary.get(key) is not None:#python2用的是row.has_key(key)
	        monitorItems[key] = dictionary.get(key)
	return monitorItems

#循环遍历字典，值是字典的话就重新排序，然后用排序后的value替换之前的value
def loop_dict(dictionary):
	for key, value in dictionary.items():
		if (type(value).__name__=='dict'):
			new_value = merge_dict(value)
			#print('key', key)
			#print('new value\n', new_value)
			dictionary[key] = new_value
			loop_dict(new_value)
		else:
			pass

def main(yuanshiname, align_res):
	global disambiguate_flag
	disambiguate_flag = '消歧标记'
	global disambiguate_id
	global name
	disambiguate_id = '消歧编号'
	name = yuanshiname #院士姓名
	global source
	source = '来源'
	global headline
	global headline2
	headline = {'jibenxinxi':'基本信息', 'renwulvli':'人物履历', 'qitazhiwu':'其他职务',
		'keyanfangxiang':'科研方向', 'yanjiulingyu':'研究领域', 'zhuyaorongyu':'主要荣誉', 
		'zhuyaochengguo':'主要成果','xueshubaogao':'学术报告', 'renwupingjia':'人物评价',
		'renwuyingxiang':'人物影响', 'gexingjiyu':'个性寄语', 'shehuizhengyi':'社会争议_争议事件', 
		'huojiangzhengyi':'获奖争议', 'yuanshiming':'院士名'}
	headline2 = {'zhongwenming':'中文名', 'waiwenming':'外文名', 'xingbie':'性别', 'chushengriqi':'出生日期', 'chushengdi':'出生地',
		'guoji':'国籍', 'minzu':'民族', 'zhiye':'职业', 'biyeyuanxiao':'毕业院校', 'zhengzhimianmao':'政治面貌', 'daibiaozuopin':'代表作品',
		'zhuyaochengjiu':'主要成就', 'cengrenzhi':'曾任职', 'xinyang':'信仰', 'yuanji':'原籍', 'jiaoyujingli':'教育经历', 'gongzuojingli':'工作经历',
		'benke':'本科', 'shuoshiyanjiusheng':'硕士研究生', 'boshiyanjiusheng':'博士研究生', 'qishishijian':'起始时间', 'jieshushijian':'结束时间',
		'xuexiaomingcheng':'学校名称', 'suoshuyuanximing':'所属院系名', 'xueli':'学历', 'xuewei':'学位', 'daoshi':'导师', 'boshihou':'博士后',
		'renzhi':'任职', 'renmian_cizhi':'任免_辞职', 'xuexiaomingcheng_keyanjigou':'学校名称_科研机构', 'suoshuyuanximing_ketizu':'所属院系名_课题组',
		'didian':'地点', 'suozaidanwei':'所在单位', 'zhicheng':'职称', 'shijiandian':'时间点', 'xinxigongbuquanweijiguan':'信息公布权威机构',
		'renmianzhiwei_zhicheng':'任免职位_职称', 'xueshujianzhi':'学术兼职', 'jishugongzuojianzhi':'技术工作兼职', 'shehuijianzhi':'社会兼职', 'zuzhijigou':'组织机构',
		'zhiwei_zhicheng':'职位_职称', 'fangxiang':'方向', 'suoyoujiangxiang':'所有奖项', 'banjiangdanwei':'颁奖单位', 'shouyujiangxiangmingcheng':'授予奖项名称',
		'xueshulunzhulei':'学术论著类', 'sanwenlei':'散文类', 'lunzhumingcheng':'论著名称', 'sanwenmingcheng':'散文名称', 'chengdanxiangmulei':'承担项目类', 'xiangmumingcheng':'项目名称',
		'yanjiuchengguolei':'研究成果类', 'yanjiuchengguomingcheng':'研究成果名称', 'famingzhuanlilei':'发明专利类', 'zhuanlimingcheng':'专利名称', 
		'rencaipeiyanglei':'人才培养类', 'jiaoyulinian_zhidaoxuesheng':'指导学生', 'yanjiang_baogaotimu':'演讲_报告题目', 'zuzhidanwei_huodongdanweimingcheng':'组织单位_活动单位名称', 
		'zhongyaoguandian':'重要观点', 'tingzhongquanti':'听众全体', 'baodaojigou':'报道机构', 'baodaorenshi':'报道人士', 'shi_jian':'事件', 'yingxiangfanweiqunti':'影响范围全体',
		'shouzhongqunti':'受众全体', 'yulu':'语录', 'xiangguancanyurenshi':'相关参与人士', 'zhengyiqiyin':'争议起因', 'shijianqiyin':'事件起因'}
	global multi_values
	multi_values = ['职业', '毕业院校', '代表作品', '主要成就', '曾任职','承担项目类','学术论著类', '研究成果类']
	global xiaoqi_list
	xiaoqi_list = [] #定义要消歧的三元组列表
	global disambiguate_id_list
	disambiguate_id_list = []
	global num
	global number
	num = 100 #消歧标记的编号 change_flag(dictionary)
	number = 0 #消歧编号
	#merge_file = 'wu_merge.json' #对齐文件的路径
	#dictionary = read_file(merge_file) #把文件读到字典中
	dictionary = align_res
	change_flag(dictionary)
	merge_change = copy.deepcopy(dictionary)
	add_delete_flag(dictionary)
	del_value(dictionary)
	#字典最多四层，删除四次
	for i in range(4):
		del_empty_array(dictionary)
	delete_json = dictionary

	#disambiguate
	find_same_flag(delete_json)
	write_keywords_to_file(xiaoqi_list)
	# 判断是否有keywords文件 有就删除
	if os.path.exists('spider1/keywords.txt'):
		os.remove('spider1/keywords.txt')
	shutil.move('keywords.txt', 'spider1') #把关键字移动到爬虫目录
	os.chdir('spider1') # 进入爬虫目录
	# 如果有items.json就删除
	if os.path.exists('items.json'):
		os.remove('items.json')
	os.system(r"scrapy crawl spider1 -o items.json") #运行爬虫
	# 保存爬虫结果
	with open('items.json','r', encoding ='utf-8') as f:
		data = json.load(f)
	os.remove('keywords.txt')
	os.remove('items.json')
	os.chdir('../') 
	disambiguate = score.score(data)

	#generate_resume
	record_id()
	find_flag(merge_change)
	delete_flag(merge_change)
	monitorItems = merge_dict(merge_change)
	loop_dict(monitorItems)
	path = 'static/xiaoqi_json/'+name+'.json'
	with open(path, 'w', encoding = 'utf-8') as file:
		json.dump(monitorItems, file, ensure_ascii = False, indent = 4)
		print("success")
	return monitorItems
	