"""Build the China AI x manufacturing dataset from raw/bundle.json (World Bank, Our World in Data/IFR, Wikipedia tables
compiled from China's National Bureau of Statistics) plus curated tables: NBS R&D by province, IFR 2025 figures, cluster companies."""
import io, json, os, numpy as np, pandas as pd

RAW, OUT = 'raw', 'out/data'
os.makedirs(OUT, exist_ok=True)
B = json.load(open(f'{RAW}/bundle.json'))
PEERS = ['CHN', 'USA', 'DEU', 'JPN', 'KOR', 'WLD']

# ------------------------------------------------------------------ national indicators, 1990 to 2025
NAMES = {'NV.IND.MANF.CD': 'manufacturing_value_added_usd', 'NV.IND.MANF.ZS': 'manufacturing_pct_gdp', 'TX.VAL.TECH.CD': 'high_tech_exports_usd',
         'TX.VAL.TECH.MF.ZS': 'high_tech_pct_manufactured_exports', 'GB.XPD.RSDV.GD.ZS': 'rd_pct_gdp', 'SP.POP.SCIE.RD.P6': 'researchers_per_million',
         'IP.PAT.RESD': 'patent_applications_residents', 'SP.POP.1564.TO': 'working_age_population'}
rows = [(c, y, col, v) for code, col in NAMES.items() for c, y, v in B[f'wb_{code}']]
nat = pd.DataFrame(rows, columns=['country', 'year', 'indicator', 'value']).pivot_table(index=['country', 'year'], columns='indicator', values='value').reset_index()
nat = nat[['country', 'year'] + list(NAMES.values())]
wld = nat[nat.country == 'WLD'].set_index('year').manufacturing_value_added_usd
nat['share_of_world_manufacturing_pct'] = (nat.manufacturing_value_added_usd / nat.year.map(wld) * 100).round(2)
rb = pd.read_csv(io.StringIO(B['owid_robots']))
rb['country'] = rb.code.replace({'OWID_WRL': 'WLD'})
rb = rb.rename(columns={'industrial_robot_installations': 'robot_installations'})[['country', 'year', 'robot_installations']]
rb['robot_installations_source'] = 'IFR via Our World in Data'
# IFR World Robotics 2026 press release (24 September 2026), installations in 2025
IFR25 = {'CHN': 354000, 'USA': 38400, 'JPN': 36219, 'KOR': 30000, 'DEU': 24842, 'WLD': 603000}
rb = pd.concat([rb, pd.DataFrame([dict(country=k, year=2025, robot_installations=v, robot_installations_source='IFR World Robotics 2026 press release') for k, v in IFR25.items()])])
nat = nat.merge(rb, on=['country', 'year'], how='outer').sort_values(['country', 'year'])
nat = nat[nat.country.isin(PEERS) & (nat.year >= 1990)].reset_index(drop=True)
nat.to_parquet(f'{OUT}/national.parquet', index=False)

# ------------------------------------------------------------------ provinces
ZH = {'Beijing': '北京', 'Tianjin': '天津', 'Hebei': '河北', 'Shanxi': '山西', 'Inner Mongolia': '内蒙古', 'Liaoning': '辽宁', 'Jilin': '吉林',
      'Heilongjiang': '黑龙江', 'Shanghai': '上海', 'Jiangsu': '江苏', 'Zhejiang': '浙江', 'Anhui': '安徽', 'Fujian': '福建', 'Jiangxi': '江西',
      'Shandong': '山东', 'Henan': '河南', 'Hubei': '湖北', 'Hunan': '湖南', 'Guangdong': '广东', 'Guangxi': '广西', 'Hainan': '海南',
      'Chongqing': '重庆', 'Sichuan': '四川', 'Guizhou': '贵州', 'Yunnan': '云南', 'Tibet': '西藏', 'Shaanxi': '陕西', 'Gansu': '甘肃',
      'Qinghai': '青海', 'Ningxia': '宁夏', 'Xinjiang': '新疆'}
# NBS, 2024 national statistical bulletin on science and technology spending (published 29 September 2025), annex table 2
RD = {'北京': (3278.4, 6.58, 6.22), '天津': (620.6, 3.44, 3.48), '河北': (967.8, 2.04, 2.00), '山西': (311.8, 1.22, 1.14), '内蒙古': (249.6, 0.95, 0.91),
      '辽宁': (730.6, 2.24, 2.15), '吉林': (231.7, 1.61, 1.51), '黑龙江': (249.6, 1.51, 1.39), '上海': (2343.7, 4.35, 3.99), '江苏': (4597.5, 3.36, 3.22),
      '浙江': (2901.4, 3.22, 3.08), '安徽': (1396.2, 2.76, 2.62), '福建': (1257.2, 2.18, 2.14), '江西': (666.3, 1.95, 1.85), '山东': (2597.3, 2.64, 2.53),
      '河南': (1275.1, 2.01, 2.00), '湖北': (1538.1, 2.56, 2.48), '湖南': (1394.6, 2.62, 2.53), '广东': (5099.6, 3.60, 3.48), '广西': (249.3, 0.87, 0.83),
      '海南': (109.6, 1.38, 1.18), '重庆': (797.3, 2.48, 2.44), '四川': (1498.8, 2.32, 2.21), '贵州': (231.1, 1.02, 0.98), '云南': (367.4, 1.17, 1.13),
      '西藏': (7.9, 0.29, 0.28), '陕西': (926.2, 2.61, 2.49), '甘肃': (164.6, 1.27, 1.27), '青海': (33.7, 0.85, 0.79), '宁夏': (95.3, 1.73, 1.59),
      '新疆': (138.5, 0.67, 0.59)}
def wtab(key, alias={}):
    t = B[key]['table']; years = [int(h[:4]) for h in t[0][1:]]; out = []
    for r in t[1:]:
        name = alias.get(r[0], r[0])
        if name not in ZH: continue
        for y, v in zip(years, r[1:]):
            if v: out.append((name, y, float(v.replace(',', ''))))
    return pd.DataFrame(out, columns=['province', 'year', key])
gdp = wtab('wiki_gdp').rename(columns={'wiki_gdp': 'gdp_cny_million'})
pc = wtab('wiki_gdppc').rename(columns={'wiki_gdppc': 'gdp_per_capita_cny'})
prov_year = gdp.merge(pc, on=['province', 'year'], how='outer').sort_values(['province', 'year']).reset_index(drop=True)
prov_year.insert(1, 'province_zh', prov_year.province.map(ZH))
prov_year.to_parquet(f'{OUT}/provinces_by_year.parquet', index=False)

CLUSTER = {'Beijing': 'Beijing', 'Guangdong': 'Shenzhen', 'Zhejiang': 'Hangzhou'}
pv = pd.DataFrame({'province': list(ZH), 'province_zh': list(ZH.values())})
pv['rd_spending_cny_100m_2024'] = pv.province_zh.map(lambda z: RD[z][0])
pv['rd_intensity_pct_2024'] = pv.province_zh.map(lambda z: RD[z][1])
pv['rd_intensity_pct_2023'] = pv.province_zh.map(lambda z: RD[z][2])
pv['share_of_national_rd_pct_2024'] = (pv.rd_spending_cny_100m_2024 / 36326.8 * 100).round(2)
g = prov_year.pivot(index='province', columns='year', values='gdp_cny_million')
p = prov_year.pivot(index='province', columns='year', values='gdp_per_capita_cny')
pv['gdp_cny_million_2025'] = pv.province.map(g[2025]); pv['gdp_per_capita_cny_2025'] = pv.province.map(p[2025])
pv['gdp_nominal_cagr_2020_2025_pct'] = pv.province.map(((g[2025] / g[2020]) ** (1 / 5) - 1) * 100).round(2)
pv['cluster'] = pv.province.map(CLUSTER)
pv.to_parquet(f'{OUT}/provinces.parquet', index=False)

# ------------------------------------------------------------------ companies in the three clusters (curated)
C = [
    ('Hangzhou', 'Alibaba Group', '阿里巴巴', 1999, 'AI models and cloud', 'Qwen models, Alibaba Cloud', 'Q1359568'),
    ('Hangzhou', 'DeepSeek', '深度求索', 2023, 'AI models and cloud', 'Open-weight language models', 'Q131577453'),
    ('Hangzhou', 'Hikvision', '海康威视', 2001, 'Vision and sensing', 'Cameras and machine vision', 'Q5760704'),
    ('Hangzhou', 'Dahua Technology', '大华股份', 2001, 'Vision and sensing', 'Cameras and machine vision', 'Q18111506'),
    ('Hangzhou', 'Hikrobot', '海康机器人', 2016, 'Robots and automation', 'Industrial cameras and mobile robots', ''),
    ('Hangzhou', 'Unitree Robotics', '宇树科技', 2016, 'Robots and automation', 'Quadruped and humanoid robots', 'Q106369174'),
    ('Hangzhou', 'DEEP Robotics', '云深处科技', 2017, 'Robots and automation', 'Quadruped robots for inspection', 'Q132447859'),
    ('Hangzhou', 'SUPCON', '中控技术', 1993, 'Robots and automation', 'Process control systems and industrial software', ''),
    ('Hangzhou', 'Geely', '吉利', 1986, 'Vehicles and devices', 'Cars and electric vehicles', 'Q739000'),
    ('Shenzhen', 'Huawei', '华为', 1987, 'Chips and compute', 'Ascend AI chips, telecoms and cloud', 'Q160120'),
    ('Shenzhen', 'Tencent', '腾讯', 1998, 'AI models and cloud', 'Hunyuan models, Tencent Cloud', 'Q860580'),
    ('Shenzhen', 'BYD', '比亚迪', 1995, 'Vehicles and devices', 'Electric vehicles and batteries', 'Q2608329'),
    ('Shenzhen', 'DJI', '大疆', 2006, 'Vehicles and devices', 'Drones and cameras', 'Q16924332'),
    ('Shenzhen', 'UBTech Robotics', '优必选', 2012, 'Robots and automation', 'Humanoid robots', 'Q65179876'),
    ('Shenzhen', 'Dobot', '越疆', 2015, 'Robots and automation', 'Collaborative robot arms', 'Q132074337'),
    ('Shenzhen', 'Leju Robotics', '乐聚机器人', 2016, 'Robots and automation', 'Humanoid robots', 'Q132767430'),
    ('Shenzhen', 'Inovance Technology', '汇川技术', 2003, 'Robots and automation', 'Drives, controllers and industrial robots', 'Q22098886'),
    ('Shenzhen', 'Foxconn Industrial Internet', '工业富联', 2015, 'Components and industrial internet', 'AI servers and smart factories', 'Q81240901'),
    ('Shenzhen', 'Sunway Communication', '信维通信', 2006, 'Components and industrial internet', 'Antennas and RF components', ''),
    ('Beijing', 'Baidu', '百度', 2000, 'AI models and cloud', 'Ernie models, Apollo autonomous driving', 'Q14772'),
    ('Beijing', 'ByteDance', '字节跳动', 2012, 'AI models and cloud', 'Doubao models, Volcano Engine cloud', 'Q55606242'),
    ('Beijing', 'Zhipu AI', '智谱', 2019, 'AI models and cloud', 'GLM language models', 'Q129572031'),
    ('Beijing', 'Moonshot AI', '月之暗面', 2023, 'AI models and cloud', 'Kimi language models', 'Q130270266'),
    ('Beijing', 'Cambricon', '寒武纪', 2016, 'Chips and compute', 'AI accelerator chips', 'Q48890160'),
    ('Beijing', 'Horizon Robotics', '地平线', 2015, 'Chips and compute', 'Driving-assistance chips and software', 'Q109351566'),
    ('Beijing', 'NAURA', '北方华创', 2001, 'Chips and compute', 'Semiconductor equipment', 'Q86728023'),
    ('Beijing', 'Xiaomi', '小米', 2010, 'Vehicles and devices', 'Phones, devices and electric cars', 'Q1636958'),
    ('Beijing', 'Galbot', '银河通用', 2023, 'Robots and automation', 'Humanoid robots', ''),
    ('Beijing', 'Mech-Mind Robotics', '梅卡曼德', 2016, 'Vision and sensing', '3D vision and robot software', 'Q117041571'),
]
co = pd.DataFrame(C, columns=['cluster', 'company', 'company_zh', 'founded', 'segment', 'what_it_does', 'wikidata'])
co.to_parquet(f'{OUT}/companies.parquet', index=False)

# ------------------------------------------------------------------ the three clusters
CL = [('Hangzhou', '杭州', 'Zhejiang', 30.274, 120.155, 'Platforms, vision and legged robots'),
      ('Shenzhen', '深圳', 'Guangdong', 22.543, 114.058, 'Hardware, devices and the electronics supply chain'),
      ('Beijing', '北京', 'Beijing', 39.904, 116.407, 'Models, chips and research')]
cl = pd.DataFrame(CL, columns=['cluster', 'cluster_zh', 'province', 'latitude', 'longitude', 'profile'])
cl = cl.merge(pv[['province', 'rd_intensity_pct_2024', 'share_of_national_rd_pct_2024', 'gdp_cny_million_2025', 'gdp_per_capita_cny_2025']], on='province')
cl['companies_listed'] = cl.cluster.map(co.cluster.value_counts())
cl.to_parquet(f'{OUT}/clusters.parquet', index=False)

ch = nat[nat.country == 'CHN'].set_index('year'); w = nat[nat.country == 'WLD'].set_index('year')
stats = dict(china_share_robots_2025=round(354000 / 603000 * 100, 1), china_share_manufacturing_2025=float(ch.loc[2025, 'share_of_world_manufacturing_pct']),
             rd_three_provinces_share=round(float(pv[pv.cluster.notna()].share_of_national_rd_pct_2024.sum()), 1), companies=len(co))
json.dump(stats, open('out/stats.json', 'w'), indent=1)
print(stats)
