#!/usr/bin/env python3
"""
Script để parse mindmap và tạo cấu trúc thứ tự cho dropdown/tree view
Giữ nguyên dữ liệu trong data.json nhưng sắp xếp theo thứ tự trong mindmap
"""

import json
import re
import os

def parse_mindmap(mindmap_path):
    """Parse mindmap file và trả về cấu trúc thứ tự"""
    with open(mindmap_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    structure = {}
    current_grade = None
    current_chapter = None
    current_model = None
    
    lines = content.split('\n')
    for line in lines:
        original_line = line
        stripped = line.strip()
        if not stripped:
            continue
        
        # Detect grade (## Khối 10)
        grade_match = re.match(r'^##\s+Khối\s+(\d+)', stripped)
        if grade_match:
            current_grade = grade_match.group(1)
            if current_grade not in structure:
                structure[current_grade] = {
                    'chapters': [],
                    'chapter_order': []
                }
            current_chapter = None
            current_model = None
            continue
        
        # Count leading spaces to determine level
        leading_spaces = len(original_line) - len(original_line.lstrip(' '))
        
        # Level 1: Chapter (0 spaces: "- **Chapter Name**")
        if leading_spaces == 0 and stripped.startswith('- **') and stripped.endswith('**'):
            chapter_name = stripped[4:-2].strip()
            if current_grade:
                if chapter_name not in structure[current_grade]['chapter_order']:
                    structure[current_grade]['chapter_order'].append(chapter_name)
                    structure[current_grade]['chapters'].append({
                        'name': chapter_name,
                        'models': [],
                        'model_order': []
                    })
                current_chapter = chapter_name
                current_model = None
            continue
        
        # Level 2: Model (2 spaces: "  - **Model Name**")
        if leading_spaces == 2 and stripped.startswith('- **') and stripped.endswith('**'):
            model_name = stripped[4:-2].strip()
            if current_grade and current_chapter:
                # Find the chapter in structure
                chapter_obj = None
                for ch in structure[current_grade]['chapters']:
                    if ch['name'] == current_chapter:
                        chapter_obj = ch
                        break
                
                if chapter_obj:
                    if model_name not in chapter_obj['model_order']:
                        chapter_obj['model_order'].append(model_name)
                        chapter_obj['models'].append({
                            'name': model_name,
                            'components': []
                        })
                    current_model = model_name
            continue
        
        # Level 3: Component (4 spaces: "    - Component Name")
        if leading_spaces == 4 and stripped.startswith('- ') and not stripped.startswith('- **'):
            component_name = stripped[2:].strip()
            if current_grade and current_chapter and current_model:
                # Find the chapter and model
                chapter_obj = None
                for ch in structure[current_grade]['chapters']:
                    if ch['name'] == current_chapter:
                        chapter_obj = ch
                        break
                
                if chapter_obj:
                    model_obj = None
                    for m in chapter_obj['models']:
                        if m['name'] == current_model:
                            model_obj = m
                            break
                    
                    if model_obj and component_name not in model_obj['components']:
                        model_obj['components'].append(component_name)
    
    return structure

def get_mindmap_order(mindmap_path):
    """Trả về thứ tự từ mindmap dưới dạng dict dễ sử dụng"""
    structure = parse_mindmap(mindmap_path)
    
    order = {
        'grades': [],
        'chapters_by_grade': {},
        'models_by_chapter': {},
        'components_by_model': {}
    }
    
    # Sort grades
    grades = sorted(structure.keys(), key=lambda x: int(x))
    order['grades'] = grades
    
    for grade in grades:
        grade_data = structure[grade]
        order['chapters_by_grade'][grade] = grade_data['chapter_order']
        
        for chapter_obj in grade_data['chapters']:
            chapter_name = chapter_obj['name']
            order['models_by_chapter'][f"{grade}::{chapter_name}"] = chapter_obj['model_order']
            
            for model_obj in chapter_obj['models']:
                model_name = model_obj['name']
                key = f"{grade}::{chapter_name}::{model_name}"
                order['components_by_model'][key] = model_obj['components']
    
    return order

if __name__ == '__main__':
    # Test
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    mindmap_path = os.path.join(project_root, 'mindmap_biovision.md')
    
    order = get_mindmap_order(mindmap_path)
    
    # Save to JSON for use in frontend
    output_path = os.path.join(project_root, 'mindmap_order.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(order, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Da parse mindmap va luu thu tu vao {output_path}")
    print(f"   - Khoi lop: {len(order['grades'])}")
    print(f"   - Chuong: {sum(len(v) for v in order['chapters_by_grade'].values())}")
    print(f"   - Mo hinh: {sum(len(v) for v in order['models_by_chapter'].values())}")
