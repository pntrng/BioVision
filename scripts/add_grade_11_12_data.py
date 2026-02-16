#!/usr/bin/env python3
"""
Script để thêm dữ liệu Khối 11 và Khối 12 vào data.json
Dựa trên thông tin từ ảnh (UID sketchfab)
"""

import json
import os
import re
from datetime import datetime, timezone

def create_id(grade, chapter, name):
    """Tạo ID duy nhất cho model"""
    # Loại bỏ dấu và ký tự đặc biệt
    def normalize(text):
        text = text.lower()
        text = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', text)
        text = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', text)
        text = re.sub(r'[ìíịỉĩ]', 'i', text)
        text = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', text)
        text = re.sub(r'[ùúụủũưừứựửữ]', 'u', text)
        text = re.sub(r'[ỳýỵỷỹ]', 'y', text)
        text = re.sub(r'[đ]', 'd', text)
        text = re.sub(r'[^a-z0-9]', '_', text)
        text = re.sub(r'_+', '_', text)
        return text.strip('_')
    
    chapter_norm = normalize(chapter)
    name_norm = normalize(name)
    # Lấy 8 ký tự đầu của UID để tạo ID ngắn gọn
    return f"{grade}_{chapter_norm}_{name_norm}"

# Dữ liệu Khối 11 từ ảnh thứ 2
grade_11_data = [
    # Trao đổi chất và chuyển hóa năng lượng ở sinh vật
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Nguyên tố đa lượng", "uid": "6e05dda8d97746c086d5b4dc8ada22f1"},
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Rễ", "uid": ""},
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Thân", "uid": "74554b702184450fbfdf3c5ace31468b"},
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Lá", "uid": ""},
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Nitrogen", "uid": ""},
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Pha sáng", "uid": ""},
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Pha tối", "uid": ""},
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Tiêu hóa chưa có cơ quan tiêu hóa", "uid": "f9a5e0b423e345cb90416ef1be1109ed"},
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Tiêu hóa trong túi tiêu hóa", "uid": ""},
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Tiêu hóa trong ống tiêu hóa", "uid": "b5b571c21077429d804354dd3f3cc308"},
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Gan", "uid": "bf6273bdf0664f8b809a27fcac8693cb"},
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Tuyến tụy, túi mật", "uid": "8acf64dc315b49308b4fcbd47e48b92b"},
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Trao đổi khí qua bề mặt cơ thể", "uid": "693db7a8e44e4b90a1afef81204459ce"},
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Trao đổi khí qua hệ thống ống khí", "uid": "e951a812971049bfbbdc3c3685a30b3f"},
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Trao đổi khí qua mang", "uid": "7bf7115377f14f138d0b99dc689c1ace"},
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Trao đổi khí qua phổi", "uid": "c0ca6af6c6a1449084341a96eea515ea"},
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Tim", "uid": "7241b29839804855a6d2cc101d73db55"},
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Hệ mạch", "uid": "50d55a6208604c1ca04d917aa4f17e3b"},
    {"chapter": "Trao đổi chất và chuyển hóa năng lượng ở sinh vật", "name": "Thận", "uid": "d3dc9bcc490c42f7a3bd9176de169e00"},
    
    # Cảm ứng ở sinh vật
    {"chapter": "Cảm ứng ở sinh vật", "name": "Hướng động", "uid": "8984903df2fb49cf99082ba9c7743136"},
    {"chapter": "Cảm ứng ở sinh vật", "name": "Hệ thần kinh dạng lưới", "uid": "46d8b5fb50654425b661d6c6f347edbc"},
    {"chapter": "Cảm ứng ở sinh vật", "name": "Hệ thần kinh dạng chuỗi hạch", "uid": "db0b1b8d18f940c4b9528f0e50001b31"},
    {"chapter": "Cảm ứng ở sinh vật", "name": "Hệ thần kinh dạng ống", "uid": "c1ba7fe29e7f44b28186e56a07502463"},
    {"chapter": "Cảm ứng ở sinh vật", "name": "Synapse", "uid": "d3be9054e57b4104b3f029cb8c6f19a9"},
    {"chapter": "Cảm ứng ở sinh vật", "name": "Neuron", "uid": "f33ea01f8e674578b55ac51d110b1721"},
    {"chapter": "Cảm ứng ở sinh vật", "name": "Mắt", "uid": "9fc8c2d381b34220a330c68876840783"},
    {"chapter": "Cảm ứng ở sinh vật", "name": "Não", "uid": "01b31600fc1140bc96394cb5ec6d6825"},
    {"chapter": "Cảm ứng ở sinh vật", "name": "Tai", "uid": "e14ca6ebb8de411695ce04eb5089266c"},
    
    # Sinh trưởng và phát triển ở sinh vật
    {"chapter": "Sinh trưởng và phát triển ở sinh vật", "name": "Phôi", "uid": "9fb225b983c14b20b67b639e17126f5b"},
    {"chapter": "Sinh trưởng và phát triển ở sinh vật", "name": "Phát triển qua biến thái", "uid": "97a185a69e25467e8931da7639c64f2e"},
    {"chapter": "Sinh trưởng và phát triển ở sinh vật", "name": "Phát triển không qua biến thái", "uid": "5ade58cf25a34a928d0c88dddba83c35"},
    
    # Sinh sản ở sinh vật
    {"chapter": "Sinh sản ở sinh vật", "name": "Hoa", "uid": "5aff81d16da5429bb66e14b0b8167780"},
    {"chapter": "Sinh sản ở sinh vật", "name": "Tinh trùng", "uid": "6a26d72b474c48f691de78b4ace9e463"},
    {"chapter": "Sinh sản ở sinh vật", "name": "Trứng", "uid": "d6b46f8a975848249edbbfb33d4882dd"},
    {"chapter": "Sinh sản ở sinh vật", "name": "Tử cung", "uid": "08d5cdbca98d452eb7660334a7ad2780"},
    
    # Mối quan hệ giữa các quá trình sinh lí...
    {"chapter": "Mối quan hệ giữa các quá trình sinh lí trong cơ thể sinh vật với một số ngành nghề liên quan đến sinh học cơ thể", "name": "Cây", "uid": "047bd0fe057547e993c56a7ebc147731"},
]

# Dữ liệu Khối 12 từ ảnh thứ nhất
grade_12_data = [
    # Di truyền phân tử
    {"chapter": "Di truyền phân tử", "name": "DNA", "uid": "4ff9b29e7952443ca050e15dff05256a"},
    {"chapter": "Di truyền phân tử", "name": "mRNA", "uid": "86d3572002254365bc52c0c034445718"},
    {"chapter": "Di truyền phân tử", "name": "tRNA", "uid": "8ab8a1d412404d73ba66ee82bdd22f4f"},
    {"chapter": "Di truyền phân tử", "name": "Phiên mã, dịch mã", "uid": "8d7833756c3d402f8572db722c735e3f"},
    
    # Di truyền NST
    {"chapter": "Di truyền NST", "name": "Cấu trúc siêu hiển vi", "uid": "16f57ae67f3a4fbdb2f4b22d80c2d10d"},
    {"chapter": "Di truyền NST", "name": "Cấu tạo NST", "uid": "2cb7bdde1f274b089eef2ca48e9c68f0"},
    {"chapter": "Di truyền NST", "name": "Allele, locus", "uid": "68881ccde9954fdeaadd74b64ea89495"},
    {"chapter": "Di truyền NST", "name": "NST đơn, kép", "uid": "8fbd0eba37b64e68993311faffb5e57b"},
    {"chapter": "Di truyền NST", "name": "Tương tác gene át chế", "uid": "f8edc1a410384141bbbc3980e5d91e9c"},
    {"chapter": "Di truyền NST", "name": "NST X", "uid": "4ab2fe1dfcba469097e2d0fe4a0f942b"},
    {"chapter": "Di truyền NST", "name": "NST Y", "uid": "388d29fb827845bfbec65dd0614c4fb7"},
    {"chapter": "Di truyền NST", "name": "Ruồi giấm", "uid": "6a4470f884554864827d848718b2b6bc"},
    {"chapter": "Di truyền NST", "name": "Bộ NST đồ của người bình thường", "uid": "caec92fcc43d4098888c981975558667"},
    
    # Mở rộng học thuyết di truyền NST
    {"chapter": "Mở rộng học thuyết di truyền NST", "name": "Lục lạp", "uid": "7f88895ea21641f9a14598a565f06ed2"},
    
    # Bằng chứng và các học thuyết tiến hóa
    {"chapter": "Bằng chứng và các học thuyết tiến hóa", "name": "Hóa thạch", "uid": "75e59d79f2a042f1aad2b6cded8b65bf"},
    {"chapter": "Bằng chứng và các học thuyết tiến hóa", "name": "Hổ phách", "uid": "53a61d58c09b4d2ab30e269aa3e22078"},
    {"chapter": "Bằng chứng và các học thuyết tiến hóa", "name": "Phát sinh loài người", "uid": "95eae619af884dafb7191945adf95b9c"},
    
    # Sinh thái học quần xã
    {"chapter": "Sinh thái học quần xã", "name": "Hệ sinh thái", "uid": "e6ae5b861c914f0bafb8a2766d899bb8"},
    {"chapter": "Sinh thái học quần xã", "name": "Chu trình nước", "uid": "033545715b344616bf08431a290d69c2"},
]

def add_models_to_data(data_file_path):
    """Thêm các model mới vào data.json"""
    # Đọc data.json hiện tại
    with open(data_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    existing_ids = set()
    existing_uids = set()
    
    # Lấy danh sách ID và UID hiện có
    for model in data.get('models', []):
        existing_ids.add(model.get('id', ''))
        if model.get('modelUid'):
            existing_uids.add(model.get('modelUid'))
    
    new_models = []
    
    # Thêm Khối 11
    for item in grade_11_data:
        if not item['uid']:  # Bỏ qua nếu không có UID
            continue
        
        model_id = create_id("11", item['chapter'], item['name'])
        # Đảm bảo ID duy nhất
        counter = 1
        original_id = model_id
        while model_id in existing_ids:
            model_id = f"{original_id}_{counter}"
            counter += 1
        
        # Bỏ qua nếu UID đã tồn tại
        if item['uid'] in existing_uids:
            try:
                print(f"[SKIP] UID {item['uid']} da ton tai: {item['name']}")
            except:
                print(f"[SKIP] UID {item['uid']} already exists")
            continue
        
        new_model = {
            "chapter": item['chapter'],
            "feature": "",  # Để trống, người dùng sẽ điền sau
            "funFact": "",  # Để trống, người dùng sẽ điền sau
            "grade": "11",
            "id": model_id,
            "items": [],  # Mảng rỗng, có thể thêm sau
            "modelUid": item['uid'],
            "name": item['name']
        }
        new_models.append(new_model)
        existing_ids.add(model_id)
        existing_uids.add(item['uid'])
    
    # Thêm Khối 12
    for item in grade_12_data:
        if not item['uid']:  # Bỏ qua nếu không có UID
            continue
        
        model_id = create_id("12", item['chapter'], item['name'])
        # Đảm bảo ID duy nhất
        counter = 1
        original_id = model_id
        while model_id in existing_ids:
            model_id = f"{original_id}_{counter}"
            counter += 1
        
        # Bỏ qua nếu UID đã tồn tại
        if item['uid'] in existing_uids:
            try:
                print(f"[SKIP] UID {item['uid']} da ton tai: {item['name']}")
            except:
                print(f"[SKIP] UID {item['uid']} already exists")
            continue
        
        new_model = {
            "chapter": item['chapter'],
            "feature": "",  # Để trống, người dùng sẽ điền sau
            "funFact": "",  # Để trống, người dùng sẽ điền sau
            "grade": "12",
            "id": model_id,
            "items": [],  # Mảng rỗng, có thể thêm sau
            "modelUid": item['uid'],
            "name": item['name']
        }
        new_models.append(new_model)
        existing_ids.add(model_id)
        existing_uids.add(item['uid'])
    
    # Thêm vào data
    data['models'].extend(new_models)
    
    # Cập nhật version và updatedAt
    current_version = data.get('version', 1)
    data['version'] = current_version + 1
    data['updatedAt'] = datetime.now(timezone.utc).isoformat()
    
    # Lưu lại
    with open(data_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"[OK] Da them {len(new_models)} model moi vao data.json")
    print(f"   - Khoi 11: {sum(1 for m in new_models if m['grade'] == '11')} model")
    print(f"   - Khoi 12: {sum(1 for m in new_models if m['grade'] == '12')} model")
    print(f"   - Version: {data['version']}")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    data_file = os.path.join(project_root, 'data.json')
    
    add_models_to_data(data_file)
