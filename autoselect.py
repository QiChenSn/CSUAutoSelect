#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中南大学自动选课系统
异步模式版本
"""

import re
import sys
import base64
import configparser
import asyncio
from typing import List, Optional
from dataclasses import dataclass

import httpx


@dataclass
class CourseConfig:
	"""课程配置数据类"""
	course_id: str
	course_type: str  # 'public' 或 'required'
	url: str


@dataclass
class LoginConfig:
	"""登录配置数据类"""
	username: str
	password: str
	semester: str


class ConfigManager:
	"""配置管理器"""
	
	def __init__(self, config_file: str = 'config.ini'):
		self.config_file = config_file
		self.config = configparser.ConfigParser()
		self.config.read(config_file, encoding='utf-8')
		
	def get_login_config(self) -> LoginConfig:
		"""获取登录配置"""
		items = dict(self.config.items('config'))
		return LoginConfig(
			username=items['username'],
			password=items['password'],
			semester=items['time']
		)
	
	def get_course_configs(self) -> List[CourseConfig]:
		"""获取课程配置列表"""
		items = dict(self.config.items('config'))
		courses = []
		
		# 公选课
		num1 = int(items.get('num1', 0))
		for i in range(1, num1 + 1):
			course_id = items[f'id{i}']
			courses.append(CourseConfig(
				course_id=course_id,
				course_type='public',
				url=f'http://csujwc.its.csu.edu.cn/jsxsd/xsxkkc/ggxxkxkOper?jx0404id={items["time"]}{course_id}&xkzy=&trjf='
			))
		
		# 必修课
		num2 = int(items.get('num2', 0))
		for i in range(1, num2 + 1):
			course_id = items[f'id_{i}']
			courses.append(CourseConfig(
				course_id=course_id,
				course_type='required',
				url=f'http://csujwc.its.csu.edu.cn/jsxsd/xsxkkc/bxqjhxkOper?jx0404id={items["time"]}{course_id}&xkzy=&trjf='
			))
		
		return courses


class CSUURLs:
	"""中南大学教务系统URL常量"""
	BASE_URL = 'http://csujwc.its.csu.edu.cn'
	VERIFY_CODE_URL = f'{BASE_URL}/jsxsd/verifycode.servlet'
	LOGIN_URL = f'{BASE_URL}/jsxsd/xk/LoginToXk'
	MAIN_URL = f'{BASE_URL}/jsxsd/framework/xsMain.jsp'
	COURSE_LIST_URL = f'{BASE_URL}/jsxsd/xsxk/xklc_list'
	COURSE_FIND_URL = 'http://csujwc.its.csu.edu.cn/jsxsd/xsxkkc/xsxkGgxxkxk?kcxx=&skls=&skxq=&skjc=&sfym=false&sfct=false&szjylb='
		

class CourseSelector:
	"""课程选择器"""
	
	def __init__(self, config_manager: ConfigManager):
		self.config_manager = config_manager
		self.login_config = config_manager.get_login_config()
		self.course_configs = config_manager.get_course_configs()
		self.client: Optional[httpx.AsyncClient] = None
		
		if not self.course_configs:
			raise ValueError('未配置任何课程ID')
	
	async def get_verify_code(self) -> str:
		"""获取验证码"""
		response = await self.client.get(CSUURLs.VERIFY_CODE_URL)
		with open('code.jpg', 'wb') as f:
			f.write(response.content)
		
		await self.client.get(CSUURLs.LOGIN_URL)  # 获取登录页面
		return input("输入验证码：")
	
	async def check_login_success(self) -> bool:
		"""检查是否登录成功，通过访问主页面并检查内容来判断"""
		try:
			# 访问主页面
			response = await self.client.get(CSUURLs.MAIN_URL)
			
			# 检查响应内容，如果包含登录页面特征，说明登录失败
			if '登录' in response.text and '用户名' in response.text:
				return False
			
			# 检查是否包含学生主页面特征
			if '学生' in response.text or 'xsMain' in response.text:
				return True
				
			# 如果都不匹配，尝试访问其他页面来判断
			test_response = await self.client.get(CSUURLs.COURSE_LIST_URL)
			if '登录' in test_response.text:
				return False
				
			return True
		except Exception as e:
			print(f"登录检测时发生错误: {e}")
			return False

	async def login(self, verify_code: str) -> bool:
		"""登录系统"""
		username_b64 = base64.b64encode(self.login_config.username.encode()).decode()
		password_b64 = base64.b64encode(self.login_config.password.encode()).decode()
		
		data = {
			'encoded': f'{username_b64}%%%{password_b64}',
			'RANDOMCODE': verify_code
		}
		
		await self.client.post(CSUURLs.LOGIN_URL, data=data)
		
		# 使用新的登录检查逻辑
		if await self.check_login_success():
			print('成功登录教务系统')
			return True
		else:
			print('学号或密码或验证码错误，请退出修改配置重启')
			return False
	
	async def enter_course_selection(self) -> bool:
		"""进入选课页面"""
		while True:
			response = await self.client.get(CSUURLs.COURSE_LIST_URL)
			keys = re.findall('href="(.+?)" target="blank">进入选课', response.text)
			
			if keys:
				await self.client.get(CSUURLs.BASE_URL + keys[0])
				print('成功进入选课页面')
				return True
			
			print('寻找选课列表中...')
			await asyncio.sleep(0.5)
	
	async def select_course(self, course_config: CourseConfig) -> bool:
		"""选择单个课程"""
		while True:
			try:
				response = await self.client.get(course_config.url)
				text = response.text
				
				if re.search('true', text):
					print(f"课程 {course_config.course_id} 成功抢课!")
					return True
				
				if re.search('冲突', text):
					match = re.search('"选课失败：(.+)"', text)
					error_msg = match.group(1) if match else "课程冲突"
					print(f"课程 {course_config.course_id} {error_msg}，已暂停该课程选课")
					return True
				
				if re.search('当前教学班已选择！', text):
					match = re.search('"选课失败：(.+)"', text)
					error_msg = match.group(1) if match else "当前教学班已选择"
					print(f"课程 {course_config.course_id} {error_msg}")
					return True
				
				if re.search('null', text):
					print(f"课程 {course_config.course_id} 没有该ID所对应的课程")
					return True
				
				await asyncio.sleep(0.5)
				
			except Exception as e:
				print(f"课程 {course_config.course_id} 发生错误: {e}")
				await asyncio.sleep(0.5)
	
	async def run(self):
		"""运行选课程序"""
		try:
			async with httpx.AsyncClient(cookies=None) as self.client:
				# 获取验证码并登录
				verify_code = await self.get_verify_code()
				if not await self.login(verify_code):
					return
				
				# 进入选课页面
				if not await self.enter_course_selection():
					return
				
				# 并发抢课
				tasks = [
					self.select_course(course_config) 
					for course_config in self.course_configs
				]
				await asyncio.gather(*tasks)
				
				print('选课已完成，程序退出')
				
		except Exception as e:
			print(f"程序运行出错: {e}")


def main():
	"""主函数"""
	try:
		# 初始化配置管理器
		config_manager = ConfigManager()
		
		# 创建选课器并运行
		selector = CourseSelector(config_manager)
		asyncio.run(selector.run())
			
	except KeyboardInterrupt:
		print("\n程序被用户中断")
	except Exception as e:
		print(f"程序启动失败: {e}")


if __name__ == '__main__':
	main()

