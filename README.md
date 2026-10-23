# China, AI and Manufacturing: Hangzhou, Shenzhen and Beijing

[Dataset on Hugging Face](https://huggingface.co/datasets/Kukai-7/china-ai-manufacturing) · code in this repository

**Where do artificial intelligence and China's factory base meet, and which places are building it?** This dataset gathers the public numbers behind that question: China's weight in world manufacturing, robots and research against four industrial peers, R&D spending in all 31 provinces, and a closer look at three clusters, Hangzhou (Zhejiang), Shenzhen (Guangdong) and Beijing.

*人工智能与中国制造：杭州、深圳、北京三大集群的公开数据。*

It was prompted by the CFA Institute article [Where AI meets manufacturing: China's next investment frontier](https://www.cfainstitute.org/insights/articles/china-ai-manufacturing-investment-opportunities) (October 2026), which argues that China's next phase is AI spread across its industrial base rather than AI as a stand-alone sector. The dataset does not take a view on that thesis or on any security; it lays out the data so the argument can be checked.

![Where China spends on research](https://huggingface.co/datasets/Kukai-7/china-ai-manufacturing/resolve/main/assets/map_rd_clusters.png)

## At a glance

| | |
|---|---|
| Countries | China, United States, Germany, Japan, South Korea and the world, 1990 to 2025 |
| National series | Manufacturing value added and share of the world, high-tech exports, R&D, researchers, patents, working-age population, robot installations |
| Provinces | 31 provinces: R&D spending and intensity 2024 (and 2023), GDP and GDP per person 2000 to 2025 |
| Clusters | Hangzhou, Shenzhen, Beijing, with their provinces' indicators |
| Companies | 29 selected companies headquartered in the three clusters, with segment and founding year |
| Format | Parquet, five configurations |

## What it shows

- **The workshop of the world.** China's share of world manufacturing value added rises from 8.5% in 2004 to about 28% from 2020; it passed the United States in 2010.
- **Robots where labour is getting scarce.** China installed 354,000 industrial robots in 2025, 59% of the world total, against 21% in 2013. Its working-age population peaked in 2015 at about 988 million.
- **From workshop to laboratory.** R&D rose from 0.9% of GDP in 2000 to 2.69% in 2024 (NBS), still below the United States, Japan, Germany and Korea in intensity but now the largest in patent applications by far (1.67 million by residents in 2024).
- **Research is concentrated.** Beijing spends 6.58% of its GDP on R&D, the highest in China; Guangdong is the largest spender in absolute terms (14% of the national total). Beijing, Guangdong and Zhejiang together account for 31% of China's R&D.
- **Three profiles.** Beijing for models, chips and research; Shenzhen for hardware, devices and the electronics supply chain; Hangzhou for platforms, vision and legged robots. Many of the robot, chip and model companies listed were founded after 2015.
- **Rich provinces spend more on research.** Across provinces, GDP per person and R&D intensity are strongly correlated (r = 0.81 on a log scale); growth from 2020 to 2025 is not.

![Robots and the workforce](https://huggingface.co/datasets/Kukai-7/china-ai-manufacturing/resolve/main/assets/robots_and_workforce.png)

![China against its peers](https://huggingface.co/datasets/Kukai-7/china-ai-manufacturing/resolve/main/assets/china_vs_peers.png)

![Three clusters compared](https://huggingface.co/datasets/Kukai-7/china-ai-manufacturing/resolve/main/assets/clusters_compared.png)

![Who builds what](https://huggingface.co/datasets/Kukai-7/china-ai-manufacturing/resolve/main/assets/companies_by_cluster.png)

![Scatter-plot matrix of the provinces](https://huggingface.co/datasets/Kukai-7/china-ai-manufacturing/resolve/main/assets/scatter_matrix_provinces.png)

## Load it

```python
from datasets import load_dataset

provinces = load_dataset("Kukai-7/china-ai-manufacturing", "provinces", split="train").to_pandas()
companies = load_dataset("Kukai-7/china-ai-manufacturing", "companies", split="train").to_pandas()

# The ten most research-intensive provinces
provinces.nlargest(10, "rd_intensity_pct_2024")[["province", "province_zh", "rd_intensity_pct_2024"]]
```

## Configurations

### `national` (default), 216 rows, 1990 to 2025

One row per country (`CHN`, `USA`, `DEU`, `JPN`, `KOR`, `WLD`) and year.

| column | description |
|---|---|
| `manufacturing_value_added_usd`, `manufacturing_pct_gdp` | World Bank, current US dollars |
| `share_of_world_manufacturing_pct` | Country value added divided by the world total, computed here |
| `high_tech_exports_usd`, `high_tech_pct_manufactured_exports` | World Bank (UN Comtrade) |
| `rd_pct_gdp`, `researchers_per_million` | World Bank (UNESCO Institute for Statistics) |
| `patent_applications_residents` | World Bank (WIPO) |
| `working_age_population` | People aged 15 to 64, World Bank (UN estimates) |
| `robot_installations`, `robot_installations_source` | Industrial robots installed in the year: IFR via Our World in Data to 2024, IFR World Robotics 2026 press release for 2025 |

### `provinces`, 31 rows

R&D spending (100 million yuan) and intensity (% of GDP) in 2024, intensity in 2023, share of national R&D, GDP and GDP per person in 2025, nominal GDP growth a year from 2020 to 2025, and `cluster` for the three cluster provinces.

### `provinces_by_year`, 248 rows

GDP (million yuan) and GDP per person (yuan) for each province in 2000, 2010 and 2020 to 2025.

### `clusters`, 3 rows

City, Chinese name, province, coordinates of the city centre, a one-line profile, the province's indicators and the number of companies listed.

### `companies`, 29 rows

Cluster, English and Chinese name, founding year, segment (AI models and cloud; chips and compute; robots and automation; vision and sensing; vehicles and devices; components and industrial internet), a short description and the Wikidata identifier when one exists.

## How it was built

1. **National series.** [World Bank Open Data](https://data.worldbank.org/) API, downloaded in October 2026.
2. **Robots.** [Our World in Data](https://ourworldindata.org/grapher/annual-industrial-robots-installed) (data from the International Federation of Robotics) to 2024; 2025 figures from the [IFR World Robotics 2026 press release](https://ifr.org/) of 24 September 2026, rounded as published.
3. **Provincial R&D.** National Bureau of Statistics of China, [2024 statistical bulletin on science and technology spending](https://www.stats.gov.cn/sj/zxfb/202509/t20250929_1961429.html) (published 29 September 2025); the provincial figures sum to the national total of 3,632.7 billion yuan.
4. **Provincial GDP.** NBS figures as compiled in the Wikipedia lists of Chinese administrative divisions by GDP and GDP per capita (revisions 1358609842 and 1373819856); 2025 values are preliminary.
5. **Companies.** Curated for this dataset from company websites and Wikipedia; Wikidata identifiers kept as references only.
6. **Charts.** Python and Matplotlib; borders from Natural Earth. The pipeline is in this repository: `collect.py`, `build.py`, `viz.py`.

## Limitations

- **Provinces, not cities.** Official R&D and GDP are at province level here. Shenzhen and Hangzhou are shown through Guangdong and Zhejiang, which include many other cities; only Beijing is a province in its own right.
- **No direct measure of AI.** There is no comparable public series for AI use in factories by province. R&D, robots and patents are proxies, not measures of AI adoption.
- **The company list is a selection.** It illustrates each cluster; it is not a ranking, not complete and not investment advice. Founding years and segments are simplified.
- **Robots in 2025 are rounded press-release figures**, and the Korean figure is approximate. IFR counts installations, not robots in use.
- **Gaps in the World Bank series.** US manufacturing stops in 2021, Japan's in 2024; R&D and researchers stop in 2022 or 2023. National (World Bank) and NBS R&D intensities differ slightly by source and year.
- **Nominal growth.** Provincial GDP growth from 2020 to 2025 is in current prices, not adjusted for inflation.
- **Correlation only.** The scatter-plot matrix has 31 points; it does not identify causes.

## Credits and licences

- World Bank (CC BY 4.0), Our World in Data (CC BY 4.0), International Federation of Robotics (press figures), National Bureau of Statistics of China, Wikipedia (CC BY-SA 4.0), Wikidata (CC0), Natural Earth (public domain).
- Thesis and framing: CFA Institute, *Where AI meets manufacturing: China's next investment frontier*, October 2026.
- This compilation, curated tables and charts: CC BY 4.0.

## Related

- [China under Deng](https://huggingface.co/datasets/Kukai-7/deng-era-china), money and growth in China, 1978 to 1997.
- [France 1980 to 2026](https://huggingface.co/datasets/Kukai-7/france-economy-1980-2026), governments, debt and the economy.
- [GitHub: Kukai-7](https://github.com/Kukai-7)
