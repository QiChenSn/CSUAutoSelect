import requests
import json
import re
import os
import time

# 配置变量 - 用户可以修改
SEMESTER = "2025-2026-1"  # 学期信息
COOKIE = "_ga=GA1.1.2104536743.1742025470; _ga_PR7953H3X6=GS2.1.s1748770182$o51$g0$t1748770182$j60$l0$h0; JSESSIONID=A4C5E4CC52D43EFAA4A73B04E343FF57; SF_cookie_350=25110820"  # Cookie信息
FORCE_GET_REQUEST = False  # 是否强制发送GET请求（即使parsed_data.json已存在）

# 教师信息列表 - 用户可以添加多个教师
# 支持三种格式：
# 1. 完整信息: {"id": "0000197", "name": "宋力"}
# 2. 只有ID: {"id": "0000197"}
# 3. 只有姓名: {"name": "宋力"}
TEACHERS = [
    {"name":"周瑄"},
    {"name":"胡敏予"},
    {"name":"李明"},
    {"name":"王秉"},
    {"name":"徐皎"},
    {"name":"纪海龙"},
    {"name":"曾元滔"},
    {"name":"熊勇清"},
    {"name":"习婷"},
    {"name":"谢旭斌"},
    {"name":"王昶"},
    {"name":"肖山"},
    {"name":"朱景婷"},
    {"name":"毛寒"},
    {"name":"唐俐娟"},
    {"name":"肖山"},
    {"name":"姚立平"},
    # 示例：只提供ID，程序会自动查找姓名
    # {"id": "0000187"},
    # 示例：只提供姓名，程序会自动查找ID
    # {"name": "宋铁（外聘）"},
    # 示例：完整信息
    # {"id": "0000424", "name": "西班牙语外教"},
]

def load_teacher_data():
    """
    从parsed_data.json加载教师数据
    """
    try:
        if os.path.exists('data/parsed_data.json'):
            with open('data/parsed_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        else:
            print("警告: data/parsed_data.json 文件不存在，请先运行GET请求获取教师列表")
            return []
    except Exception as e:
        print(f"加载教师数据时发生错误: {e}")
        return []

def check_teacher_data_freshness():
    """
    检查教师数据是否需要更新
    """
    if not os.path.exists('data/parsed_data.json'):
        return True  # 文件不存在，需要获取
    
    try:
        # 检查文件修改时间
        file_time = os.path.getmtime('data/parsed_data.json')
        import time
        current_time = time.time()
        
        # 如果文件超过24小时，建议更新
        if current_time - file_time > 24 * 3600:
            print("提示: parsed_data.json 文件已超过24小时，建议设置 FORCE_GET_REQUEST = True 重新获取最新数据")
            return False  # 不强制更新，但给出提示
        
        return False  # 文件较新，不需要更新
    except Exception:
        return False  # 出错时默认不更新

def complete_teacher_info(teacher_list):
    """
    自动补全教师信息
    """
    teacher_data = load_teacher_data()
    if not teacher_data:
        return teacher_list
    
    completed_teachers = []
    
    for teacher in teacher_list:
        completed_teacher = teacher.copy()
        
        # 如果只有ID，查找对应的姓名
        if 'id' in teacher and 'name' not in teacher:
            for teacher_info in teacher_data:
                if teacher_info.get('jg0101id') == teacher['id']:
                    completed_teacher['name'] = teacher_info.get('xm', '')
                    break
            else:
                continue
        
        # 如果只有姓名，查找对应的ID
        elif 'name' in teacher and 'id' not in teacher:
            for teacher_info in teacher_data:
                if teacher_info.get('xm') == teacher['name']:
                    completed_teacher['id'] = teacher_info.get('jg0101id', '')
                    break
            else:
                continue
        
        # 如果信息完整，验证是否存在
        elif 'id' in teacher and 'name' in teacher:
            found = False
            for teacher_info in teacher_data:
                if (teacher_info.get('jg0101id') == teacher['id'] and 
                    teacher_info.get('xm') == teacher['name']):
                    found = True
                    break
            if not found:
                continue
        
        # 如果信息不完整，跳过
        else:
            continue
        
        completed_teachers.append(completed_teacher)
    
    return completed_teachers

def make_get_request():
    """
    发送GET请求到中南大学教务系统
    """
    # 请求URL
    url = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_find_jg0101.jsp"
    
    # 请求参数
    params = {
        'xnxq01id': SEMESTER,
        'init': '1',
        'isview': '1'
    }
    
    # 请求头
    headers = {
        'Host': 'csujwc.its.csu.edu.cn',
        'Proxy-Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Referer': f'http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_find_xx04.jsp?init=1&xx04id=&isview=1&xnxq01id={SEMESTER}',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': COOKIE
    }
    
    try:
        # 发送GET请求
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        # 如果响应成功
        if response.status_code == 200:
            print("✓ GET请求成功")
            
            # 解析JavaScript数据
            parse_js_data(response.text)
            
        else:
            print(f"✗ GET请求失败，状态码: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

def parse_js_data(html_content):
    """
    解析HTML中的JavaScript数据
    """
    try:
        # 查找JavaScript数组数据
        pattern = r'var\s+js\s*=\s*"(\[.*?\])"'
        match = re.search(pattern, html_content, re.DOTALL)
        
        if match:
            js_data_str = match.group(1)
            # 替换JavaScript对象格式为JSON格式
            js_data_str = js_data_str.replace("'", '"')
            js_data_str = re.sub(r'(\w+):', r'"\1":', js_data_str)
            
            # 解析JSON数据
            data = json.loads(js_data_str)
            
            # 格式化保存到文件
            with open('data/parsed_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ 解析到 {len(data)} 位教师信息")
            
        else:
            print("✗ 未找到教师数据")
            
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
    except Exception as e:
        print(f"解析数据时发生错误: {e}")

def parse_course_data(html_content, teacher_name):
    """
    解析课程信息数据
    """
    try:
        # 查找所有课程信息div - 更宽松的匹配模式
        pattern = r'<div[^>]*style="display:\s*none;"[^>]*class="kbcontent"[^>]*>(.*?)</div>'
        matches = re.findall(pattern, html_content, re.DOTALL)
        
        # 如果没有找到，尝试其他可能的模式
        if not matches:
            pattern = r'<div[^>]*class="kbcontent"[^>]*style="display:\s*none;"[^>]*>(.*?)</div>'
            matches = re.findall(pattern, html_content, re.DOTALL)
        
        courses = []
        for match in matches:
            course_info = {}
            
            # 定义字段映射
            field_mappings = {
                '课程名称': r'<font title=\'课程名称\'>([^<]+)</font>',
                '选课人数': r'<font title=\'选课人数\'>(\d+)人</font>',
                '周次': r'<font title=\'周次\'>([^<]+)</font>',
                '节次': r'<font title=\'节次\'>([^<]+)</font>',
                '上课地点': r'<font title=\'上课地点教室\'>([^<]+)</font>',
                '上课总学时': r'<font title=\'上课总学时\'>(\d+)</font>',
                '课程性质': r'<font title=\'课程性质\'>([^<]+)</font>',
                '行政班级名称': r'<font title=\'行政班级名称\'>([^<]+)</font>'
            }
            
            # 提取常规字段
            for field_name, pattern in field_mappings.items():
                match_result = re.search(pattern, match)
                if match_result:
                    value = match_result.group(1)
                    # 特殊处理数字字段
                    if field_name in ['选课人数', '上课总学时']:
                        course_info[field_name] = int(value)
                    else:
                        course_info[field_name] = value
            
            # 特殊处理教学班名称 - 支持多种格式
            class_name_patterns = [
                r'<font title=\'教学班名称\'>([^<]+)<br/></font>',  # 带<br/>的格式
                r'<font title=\'教学班名称\'>([^<]+)</font>',       # 标准格式
            ]
            
            for pattern in class_name_patterns:
                class_name_match = re.search(pattern, match)
                if class_name_match:
                    course_info['教学班名称'] = class_name_match.group(1)
                    break
            
            if course_info:  # 只添加有数据的课程
                # 只保留包含"网上慕课"的课程
                if '教学班名称' in course_info and '网上慕课' in course_info['教学班名称']:
                    # 提取课程ID
                    course_id_match = re.search(r'网上慕课-(\d{6})', course_info['教学班名称'])
                    if course_id_match:
                        course_info['课程ID'] = course_id_match.group(1)
                    courses.append(course_info)
        
        if courses:
            print(f"✓ 找到 {len(courses)} 门网上慕课课程")
        else:
            print("✗ 未找到网上慕课课程")
        
        return courses
            
    except Exception as e:
        print(f"解析课程数据时发生错误: {e}")
        return []

def make_post_request():
    """
    发送POST请求到中南大学教务系统
    """
    # 自动补全教师信息
    completed_teachers = complete_teacher_info(TEACHERS)
    
    if not completed_teachers:
        print("✗ 没有有效的教师信息")
        return
    
    print(f"查询 {len(completed_teachers)} 位教师...")
    
    # 请求URL
    url = "http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_kb.jsp"
    
    # 统计变量
    all_courses = []
    teachers_with_courses = []
    teachers_without_courses = []
    
    # 为每个教师发送请求
    for teacher in completed_teachers:
        print(f"查询教师: {teacher['name']}", end=" ")
        
        # POST数据
        data = {
            'type': 'jg0101',
            'isview': '1',
            'zc': '',
            'xnxq01id': SEMESTER,
            'yxbh': '',
            'jszwdm': '',
            'teacherID': teacher['name'],
            'jg0101id': teacher['id'],
            'jg0101mc': '',
            'sfFD': '1'
        }
        
        # 请求头
        headers = {
            'Host': 'csujwc.its.csu.edu.cn',
            'Proxy-Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Origin': 'http://csujwc.its.csu.edu.cn',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Referer': f'http://csujwc.its.csu.edu.cn/jiaowu/pkgl/llsykb/llsykb_find_jg0101.jsp?xnxq01id={SEMESTER}&init=1&isview=1',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cookie': COOKIE
        }
        
        try:
            # 发送POST请求
            response = requests.post(url, data=data, headers=headers, timeout=10)
            
            # 如果响应成功
            if response.status_code == 200:
                # 解析课程信息
                courses = parse_course_data(response.text, teacher['name'])
                
                # 统计信息
                if courses:
                    teachers_with_courses.append(teacher['name'])
                    # 为每个课程添加教师信息
                    for course in courses:
                        course['教师姓名'] = teacher['name']
                        course['教师ID'] = teacher['id']
                    all_courses.extend(courses)
                else:
                    teachers_without_courses.append(teacher['name'])
                
            else:
                print("✗ 请求失败")
                teachers_without_courses.append(teacher['name'])
                
        except requests.exceptions.RequestException as e:
            print("✗ 网络错误")
            teachers_without_courses.append(teacher['name'])
        except Exception as e:
            print("✗ 解析错误")
            teachers_without_courses.append(teacher['name'])
    
    # 生成汇总报告
    generate_summary_report(all_courses, teachers_with_courses, teachers_without_courses)

def generate_summary_report(all_courses, teachers_with_courses, teachers_without_courses):
    """
    生成汇总报告
    """
    print("\n" + "="*50)
    print("查询结果汇总报告")
    print("="*50)
    
    # 保存所有课程信息到汇总文件
    if all_courses:
        summary_filename = 'data/all_online_courses_summary.json'
        with open(summary_filename, 'w', encoding='utf-8') as f:
            json.dump(all_courses, f, ensure_ascii=False, indent=2)
        print(f"✓ 所有网上慕课课程已汇总保存到: {summary_filename}")
        print(f"✓ 总共找到 {len(all_courses)} 门网上慕课课程")
        
        # 生成config格式的课程ID
        generate_config_format(all_courses)
    else:
        print("✗ 未找到任何网上慕课课程")
    
    # 统计有课程的教师
    if teachers_with_courses:
        print(f"\n✓ 以下 {len(teachers_with_courses)} 位教师有网上慕课课程:")
        for i, teacher in enumerate(teachers_with_courses, 1):
            print(f"  {i}. {teacher}")
    else:
        print("\n✗ 没有教师有网上慕课课程")
    
    # 统计没有课程的教师
    if teachers_without_courses:
        print(f"\n✗ 以下 {len(teachers_without_courses)} 位教师没有查询到网上慕课课程:")
        for i, teacher in enumerate(teachers_without_courses, 1):
            print(f"  {i}. {teacher}")
    else:
        print("\n✓ 所有教师都有网上慕课课程")
    
    # 总体统计
    total_teachers = len(teachers_with_courses) + len(teachers_without_courses)
    print(f"\n总体统计:")
    print(f"  总教师数: {total_teachers}")
    print(f"  有课程教师数: {len(teachers_with_courses)}")
    print(f"  无课程教师数: {len(teachers_without_courses)}")
    print(f"  总课程数: {len(all_courses)}")
    
    print("="*50)

def generate_config_format(all_courses):
    """
    生成config格式的课程ID配置
    """
    # 提取所有课程ID
    course_ids = []
    for course in all_courses:
        if '课程ID' in course:
            course_ids.append({
                'id': course['课程ID'],
                'name': course['课程名称'],
                'teacher': course['教师姓名']
            })
    
    if course_ids:
        # 去重并排序
        unique_courses = []
        seen_ids = set()
        for course in course_ids:
            if course['id'] not in seen_ids:
                unique_courses.append(course)
                seen_ids.add(course['id'])
        
        # 按ID排序
        unique_courses.sort(key=lambda x: x['id'])
        
        # 生成config格式
        config_filename = 'data/course_ids_config.txt'
        with open(config_filename, 'w', encoding='utf-8') as f:
            f.write(f"# 网上慕课课程ID配置\n")
            f.write(f"# 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 总课程数: {len(unique_courses)}\n\n")
            f.write(f"num1 = {len(unique_courses)}\n")
            
            for i, course in enumerate(unique_courses, 1):
                f.write(f"id{i} = {course['id']}\n")
        
        print(f"✓ 课程ID配置已保存到: {config_filename}")
        print(f"✓ 共提取到 {len(unique_courses)} 个唯一课程ID")
        
        # 显示课程ID列表
        print("\n课程ID列表:")
        for i, course in enumerate(unique_courses, 1):
            print(f"  id{i} = {course['id']} ({course['name']} - {course['teacher']})")
    else:
        print("✗ 未找到有效的课程ID")

if __name__ == "__main__":
    print("中南大学教务系统课程查询")
    print("="*40)
    
    # 检查是否需要发送GET请求
    need_get_request = FORCE_GET_REQUEST or not os.path.exists('data/parsed_data.json')
    
    if need_get_request:
        print("获取教师列表...")
        make_get_request()
    else:
        print("使用现有教师列表")
        # 检查数据是否需要更新
        check_teacher_data_freshness()
    
    print("\n查询网上慕课课程...")
    make_post_request()
