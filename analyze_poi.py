import pandas as pd

# 读取Excel文件
df = pd.read_excel('高德POI分类与编码（中英文）_V1.06_20230208.xlsx')

# 筛选餐饮相关数据
food_df = df[df['大类'].str.contains('餐饮', na=False)]

print('=' * 60)
print('高德POI餐饮分类编码分析')
print('=' * 60)
print(f'餐饮分类总记录数: {len(food_df)}')
print()

# 按中类分组输出
for mid_type in sorted(food_df['中类'].unique()):
    sub_df = food_df[food_df['中类'] == mid_type]
    print(f'【{mid_type}】')
    for _, row in sub_df.iterrows():
        code = row['NEW_TYPE']
        name = row['小类']
        en_name = row['Sub Category']
        print(f'  {code:6d} - {name} ({en_name})')
    print()
