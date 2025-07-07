#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
课程查找工具使用示例
"""

from course_finder import CourseFinder


def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 创建课程查找器实例
    finder = CourseFinder()
    
    try:
        # 获取所有课程
        print("1. 获取所有课程信息...")
        all_courses = finder.get_teacher_courses()
        print(f"总共找到 {len(all_courses)} 门课程")
        
        # 显示前5门课程
        if all_courses:
            print("\n前5门课程信息:")
            finder.print_course_info(all_courses[:5])
        
        # 按课程名称搜索
        print("\n2. 搜索包含'数学'的课程...")
        math_courses = finder.search_course_by_name("数学")
        finder.print_course_info(math_courses)
        
        # 按教师姓名搜索
        print("\n3. 搜索特定教师的课程...")
        # 这里需要替换为实际的教师姓名
        teacher_courses = finder.search_course_by_teacher("张")
        finder.print_course_info(teacher_courses)
        
        # 保存到文件
        print("\n4. 保存课程信息到文件...")
        if all_courses:
            finder.save_to_json(all_courses, "all_courses.json")
            finder.save_to_csv(all_courses, "all_courses.csv")
        
    except Exception as e:
        print(f"示例运行出错: {e}")
    finally:
        finder.close_session()


def example_advanced_search():
    """高级搜索示例"""
    print("\n=== 高级搜索示例 ===")
    
    finder = CourseFinder()
    
    try:
        # 获取所有课程
        all_courses = finder.get_teacher_courses()
        
        # 自定义过滤条件
        print("1. 查找学分大于2的课程...")
        high_credit_courses = [
            course for course in all_courses 
            if course.credits and float(course.credits) > 2
        ]
        finder.print_course_info(high_credit_courses)
        
        # 查找特定地点的课程
        print("\n2. 查找在特定教室的课程...")
        location_courses = [
            course for course in all_courses 
            if course.location and "教学楼" in course.location
        ]
        finder.print_course_info(location_courses)
        
        # 统计信息
        print("\n3. 课程统计信息:")
        if all_courses:
            teachers = set(course.teacher_name for course in all_courses if course.teacher_name)
            locations = set(course.location for course in all_courses if course.location)
            
            print(f"总课程数: {len(all_courses)}")
            print(f"教师数量: {len(teachers)}")
            print(f"上课地点数量: {len(locations)}")
            
            # 显示前几个教师
            print(f"部分教师: {', '.join(list(teachers)[:5])}")
        
    except Exception as e:
        print(f"高级搜索示例运行出错: {e}")
    finally:
        finder.close_session()


def example_batch_processing():
    """批量处理示例"""
    print("\n=== 批量处理示例 ===")
    
    finder = CourseFinder()
    
    try:
        # 获取所有课程
        all_courses = finder.get_teacher_courses()
        
        # 按教师分组
        teacher_courses = {}
        for course in all_courses:
            if course.teacher_name:
                if course.teacher_name not in teacher_courses:
                    teacher_courses[course.teacher_name] = []
                teacher_courses[course.teacher_name].append(course)
        
        # 显示每个教师的课程数量
        print("各教师课程数量:")
        for teacher, courses in sorted(teacher_courses.items()):
            print(f"{teacher}: {len(courses)} 门课程")
        
        # 保存每个教师的课程到单独文件
        print("\n保存各教师课程信息...")
        for teacher, courses in teacher_courses.items():
            if len(courses) > 0:
                filename = f"teacher_{teacher}_courses.json"
                finder.save_to_json(courses, filename)
        
    except Exception as e:
        print(f"批量处理示例运行出错: {e}")
    finally:
        finder.close_session()


if __name__ == "__main__":
    print("课程查找工具使用示例")
    print("=" * 50)
    
    # 运行基本示例
    example_basic_usage()
    
    # 运行高级搜索示例
    example_advanced_search()
    
    # 运行批量处理示例
    example_batch_processing()
    
    print("\n所有示例运行完成！") 