import json, os, glob, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly, Patch
from matplotlib.lines import Line2D
from shapely.geometry import shape, box

for f in glob.glob('fonts/*.otf') + ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc']:
    if os.path.exists(f): fm.fontManager.addfont(f)
_n = {f.name for f in fm.fontManager.ttflist}
FONT = next((n for n in ('Noto Sans CJK SC', 'Noto Sans CJK JP') if n in _n), 'DejaVu Sans')
plt.rcParams.update({'font.family': FONT, 'font.size': 10, 'axes.edgecolor': '#BBBBBB', 'axes.linewidth': .6,
                     'xtick.color': '#666666', 'ytick.color': '#666666', 'axes.labelcolor': '#444444', 'text.color': '#1F1F1F',
                     'savefig.dpi': 200})
INK, MID, LIGHT, LAND, PAPER = '#1F1F1F', '#8A8A8A', '#C9C6BF', '#ECE9E3', '#FFFFFF'
RED, RED_SOFT, BLUE, BLUE_SOFT = '#B33A2B', '#E3B5AE', '#2F4B7C', '#B9C4D6'
os.makedirs('out/assets', exist_ok=True)

nat = pd.read_parquet('out/data/national.parquet')
pv = pd.read_parquet('out/data/provinces.parquet')
co = pd.read_parquet('out/data/companies.parquet')
cl = pd.read_parquet('out/data/clusters.parquet')
CLN = ['Hangzhou', 'Shenzhen', 'Beijing']
CCOL = {'Hangzhou': RED, 'Shenzhen': BLUE, 'Beijing': INK}
CLP = {'Beijing': 'Beijing', 'Shenzhen': 'Guangdong', 'Hangzhou': 'Zhejiang'}

def title(fig, t, s, y=.95):
    fig.text(.05, y, t, fontsize=15, weight='bold')
    fig.text(.05, y - .045, s, fontsize=9, color='#555555')
def clean(ax, left=True):
    for s_ in ('top', 'right'): ax.spines[s_].set_visible(False)
    if not left: ax.spines['left'].set_visible(False)
    ax.tick_params(length=0)
def ser(c, col):
    s = nat[nat.country == c].set_index('year')[col].dropna(); return s

# ------------------------------------------------------------------ 1. map: R&D intensity by province, the three clusters
EXT = (73, 135.5, 17.5, 54)
clip = box(EXT[0] - 2, EXT[2] - 2, EXT[1] + 2, EXT[3] + 2)
fig, ax = plt.subplots(figsize=(11, 8.2))
for f in json.load(open('raw/ne_50m_admin_0_countries.geojson'))['features']:
    if f['properties']['ADM0_A3'] == 'CHN': continue
    g = shape(f['geometry'])
    if not g.intersects(clip): continue
    for p in getattr(g.intersection(clip), 'geoms', [g.intersection(clip)]):
        if p.geom_type == 'Polygon': ax.add_patch(MPoly(np.array(p.exterior.coords), closed=True, fc='#F5F3EF', ec='#E2DFD9', lw=.4))
BINS = [(0, 1, '#F1EEE9'), (1, 1.5, '#DCE1EA'), (1.5, 2.5, '#B9C4D6'), (2.5, 3, '#8197B7'), (3, 4, '#4D6894'), (4, 99, '#1E3358')]
def colour(v): return next(c for lo, hi, c in BINS if lo <= v < hi)
zh = dict(zip(pv.province_zh, pv.rd_intensity_pct_2024))
for f in json.load(open('raw/china_provinces.geojson'))['features']:
    v = next(val for k, val in zh.items() if f['properties']['name_zh'].startswith(k))
    g = shape(f['geometry'])
    for p in getattr(g, 'geoms', [g]):
        ax.add_patch(MPoly(np.array(p.exterior.coords), closed=True, fc=colour(v), ec=PAPER, lw=.6))
for _, r in cl.iterrows():
    ax.scatter(r.longitude, r.latitude, s=150, marker='o', fc='none', ec=RED, lw=1.8, zorder=5)
    ax.scatter(r.longitude, r.latitude, s=14, c=RED, zorder=6)
LBL = {'Beijing': (-12, 10, 'right'), 'Hangzhou': (14, -2, 'left'), 'Shenzhen': (12, -16, 'left')}
for _, r in cl.iterrows():
    dx, dy, ha = LBL[r.cluster]
    ax.annotate(f'{r.cluster} {r.cluster_zh}\n' + ('' if r.cluster == 'Beijing' else f'{CLP[r.cluster]}: ') + f'R&D {r.rd_intensity_pct_2024:.2f}% of GDP', (r.longitude, r.latitude), xytext=(dx, dy),
                textcoords='offset points', ha=ha, fontsize=8.5, color=RED, weight='bold', zorder=7,
                bbox=dict(fc=PAPER, ec='none', alpha=.85, pad=1.5))
ax.annotate('Shanghai 4.35%', (121.47, 31.23), xytext=(40, 16), textcoords='offset points', fontsize=7.5, color=INK, arrowprops=dict(arrowstyle='-', color=MID, lw=.6))
ax.annotate('Jiangsu 3.36%', (119.4, 33.2), xytext=(30, 22), textcoords='offset points', fontsize=7.5, color=INK, arrowprops=dict(arrowstyle='-', color=MID, lw=.6))
ax.set_xlim(EXT[0], EXT[1]); ax.set_ylim(EXT[2], EXT[3]); ax.set_aspect(1 / np.cos(np.radians(35)))
ax.set_xticks([]); ax.set_yticks([])
for s_ in ax.spines.values(): s_.set_visible(False)
labs = ['under 1%', '1 to 1.5%', '1.5 to 2.5%', '2.5 to 3%', '3 to 4%', '4% and above']
ax.legend([Patch(fc=c, ec='none') for _, _, c in BINS] + [Line2D([], [], marker='o', ls='', mfc='none', mec=RED, mew=1.8, ms=11)],
          labs + ['Cluster city'], loc='lower left', frameon=False, fontsize=8.5, title='R&D spending, % of GDP, 2024', title_fontsize=8.5, alignment='left')
title(fig, 'Where China spends on research', 'R&D spending as a share of provincial GDP in 2024 (national average 2.69%), with the three AI and manufacturing clusters.', y=.955)
fig.text(.05, .03, 'Data: National Bureau of Statistics of China, 2024 statistical bulletin on science and technology spending. Borders: Natural Earth. '
         'Province-level data, not city-level. Hong Kong, Macau and Taiwan not covered.', fontsize=7, color=MID)
plt.subplots_adjust(left=.02, right=.98, top=.89, bottom=.05)
fig.savefig('out/assets/map_rd_clusters.png', facecolor=PAPER); plt.close(fig)

# ------------------------------------------------------------------ 2. robots and the shrinking workforce
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.5, 5.2), gridspec_kw=dict(width_ratios=[1.45, 1], wspace=.28))
w, c = ser('WLD', 'robot_installations'), ser('CHN', 'robot_installations')
yrs = [y for y in w.index if y in c.index]
a1.bar(yrs, w[yrs] / 1e3, color=LIGHT, width=.72, label='Rest of the world')
a1.bar(yrs, c[yrs] / 1e3, color=RED, width=.72, label='China')
for y in yrs:
    if y in (2013, 2017, 2021, 2024, 2025): a1.text(y, w[y] / 1e3 + 8, f'{c[y] / w[y] * 100:.0f}%', ha='center', fontsize=8, color=RED)
a1.text(yrs[0] - .4, 640, 'Labels: China share of world installations', fontsize=7.5, color=MID)
a1.set_ylim(0, 670); a1.set_ylabel('Industrial robots installed (thousands)'); a1.set_xticks(yrs[::2]); clean(a1)
a1.yaxis.grid(color='#EEEEEE', lw=.6); a1.set_axisbelow(True); a1.legend(frameon=False, loc='upper left', bbox_to_anchor=(0, .95), fontsize=8.5)
a1.set_title('China installs more robots than the rest of the world combined', fontsize=10, loc='left', color=INK)
wp = ser('CHN', 'working_age_population') / 1e6
a2.plot(wp.index, wp, color=INK, lw=1.8)
pk = wp.idxmax(); a2.scatter([pk], [wp[pk]], c=RED, s=22, zorder=3)
a2.annotate(f'Peak {pk}: {wp[pk]:.0f} m', (pk, wp[pk]), xytext=(-10, 10), textcoords='offset points', ha='right', fontsize=8, color=RED)
last = wp.index.max(); a2.annotate(f'{last}: {wp[last]:.0f} m', (last, wp[last]), xytext=(-4, -16), textcoords='offset points', ha='right', fontsize=8)
a2.set_ylabel('People aged 15 to 64 (millions)'); clean(a2); a2.yaxis.grid(color='#EEEEEE', lw=.6)
a2.set_title('Fewer workers: the working-age population is past its peak', fontsize=10, loc='left', color=INK)
title(fig, 'Robots where labour is getting scarce', 'Industrial robot installations, 2011 to 2025, and China\'s working-age population since 1990.', y=.95)
fig.text(.05, .02, 'Data: International Federation of Robotics via Our World in Data (to 2024); IFR World Robotics 2026 press release (2025, rounded). '
         'World Bank (population, UN estimates and projections).', fontsize=7, color=MID)
plt.subplots_adjust(left=.06, right=.98, top=.78, bottom=.1)
fig.savefig('out/assets/robots_and_workforce.png', facecolor=PAPER); plt.close(fig)

# ------------------------------------------------------------------ 3. peers: share of world manufacturing, R&D, researchers, patents
STY = {'CHN': (RED, 2.2, 'China'), 'USA': (BLUE, 1.5, 'United States'), 'JPN': (INK, 1.2, 'Japan'), 'DEU': (MID, 1.2, 'Germany'), 'KOR': (BLUE_SOFT, 1.5, 'South Korea')}
fig, axs = plt.subplots(2, 2, figsize=(12.5, 8.6), gridspec_kw=dict(hspace=.42, wspace=.22))
PAN = [('share_of_world_manufacturing_pct', 'Share of world manufacturing value added (%)', 1, False),
       ('rd_pct_gdp', 'R&D spending (% of GDP)', 1, False),
       ('researchers_per_million', 'Researchers per million people', 1, False),
       ('patent_applications_residents', 'Patent applications by residents (thousands, log scale)', 1e3, True)]
for ax, (col, t, k, lg) in zip(axs.flat, PAN):
    ends = []
    for cc, (colr, lw, name) in STY.items():
        s = ser(cc, col) / k
        if len(s) == 0: continue
        ax.plot(s.index, s, color=colr, lw=lw, label=name)
        ends.append((s.index[-1], s.iloc[-1], colr))
    if lg: ax.set_yscale('log')
    ax.figure.canvas.draw()
    pts = sorted([(ax.transData.transform((x, y))[1], x, y, c_) for x, y, c_ in ends])
    last = -1e9
    for py, x, y, c_ in pts:
        py2 = max(py, last + 12); last = py2
        ax.annotate(f'{y:,.1f}' if y < 100 else f'{y:,.0f}', (x, y), xytext=(4, (py2 - py) / ax.figure.dpi * 72), textcoords='offset points', fontsize=7.5, color=c_, va='center')
    ax.set_title(t, fontsize=10, loc='left'); clean(ax); ax.yaxis.grid(color='#EEEEEE', lw=.6); ax.set_xlim(1990, 2027.5)
axs[0, 0].legend(frameon=False, fontsize=8.5, loc='upper left')
title(fig, 'From workshop to laboratory', 'China against four industrial peers, 1990 to latest year. China passed the United States in manufacturing output in 2010.', y=.965)
fig.text(.05, .02, 'Data: World Bank, World Development Indicators (manufacturing value added in current US dollars; R&D and researchers from UNESCO; patents from WIPO). '
         'Series end where the World Bank stops reporting, e.g. US manufacturing after 2021.', fontsize=7, color=MID)
plt.subplots_adjust(left=.06, right=.96, top=.86, bottom=.07)
fig.savefig('out/assets/china_vs_peers.png', facecolor=PAPER); plt.close(fig)

# ------------------------------------------------------------------ 4. the three clusters compared
fig, axs = plt.subplots(1, 4, figsize=(13, 5), gridspec_kw=dict(wspace=.5))
nat_pc = (pv.gdp_cny_million_2025.sum() * 1e6) / (pv.gdp_cny_million_2025 / pv.gdp_per_capita_cny_2025 * 1e6).sum()
ch = nat[nat.country == 'CHN'].set_index('year')
METR = [('rd_intensity_pct_2024', 'R&D,\n% of GDP, 2024', 2.69, '{:.2f}%', 'China 2.69%'),
        ('share_of_national_rd_pct_2024', 'Share of\nChina\'s R&D, 2024', None, '{:.1f}%', None),
        ('gdp_per_capita_cny_2025', 'GDP per person,\n2025 (thousand yuan)', nat_pc / 1e3, '{:.0f}', f'China {nat_pc / 1e3:.0f}'),
        ('gdp_nominal_cagr_2020_2025_pct', 'Nominal GDP growth,\n% a year, 2020 to 2025', None, '{:.1f}%', None)]
p3 = pv.set_index('province').loc[[CLP[c] for c in CLN]]
for ax, (col, t, ref, fmt, rl) in zip(axs, METR):
    v = p3[col] / (1e3 if 'per_capita' in col else 1)
    ax.barh(range(3), v, color=[CCOL[c] for c in CLN], height=.6)
    for i, x in enumerate(v): ax.text(x, i, ' ' + fmt.format(x), va='center', fontsize=9)
    if ref is not None:
        ax.axvline(ref, color=MID, lw=.8, ls=(0, (3, 2))); ax.text(ref, 2.55, rl, fontsize=7.5, color=MID, ha='center')
    ax.set_yticks(range(3)); ax.set_yticklabels([f'{c}\n({CLP[c]})' if c != 'Beijing' else c for c in CLN] if ax is axs[0] else [])
    ax.invert_yaxis(); ax.set_xticks([]); clean(ax, left=False); ax.set_title(t, fontsize=9.5, loc='left', pad=14); ax.set_xlim(0, v.max() * 1.35)
title(fig, 'Three clusters, three profiles', 'Beijing is research-heavy, Guangdong is the largest R&D spender, Zhejiang grew fastest of the three. Together they make up 31% of China\'s R&D.', y=.95)
fig.text(.05, .03, 'Data: NBS (R&D, 2024); provincial GDP from NBS via Wikipedia (2025 preliminary). Shenzhen and Hangzhou are shown through their provinces '
         '(Guangdong, Zhejiang): city figures are not in this dataset.', fontsize=7, color=MID)
plt.subplots_adjust(left=.09, right=.98, top=.72, bottom=.1)
fig.savefig('out/assets/clusters_compared.png', facecolor=PAPER); plt.close(fig)

# ------------------------------------------------------------------ 5. who builds what: the companies, by cluster and founding year
SEG = ['AI models and cloud', 'Chips and compute', 'Robots and automation', 'Vision and sensing', 'Vehicles and devices', 'Components and industrial internet']
MK = dict(zip(SEG, ['o', 's', 'D', '^', 'v', 'P']))
fig, axs = plt.subplots(1, 3, figsize=(13.5, 6.6), sharex=True, gridspec_kw=dict(wspace=.8))
for ax, cn, colr in zip(axs, ['Hangzhou', 'Shenzhen', 'Beijing'], [RED, BLUE, INK]):
    d = co[co.cluster == cn].sort_values(['founded', 'company']).reset_index(drop=True)
    ax.hlines(range(len(d)), 1984, d.founded, color='#EEEEEE', lw=.8)
    for i, r in d.iterrows():
        ax.scatter(r.founded, i, marker=MK[r.segment], s=46, c=colr, zorder=3)
        ax.text(r.founded + .8 if r.founded < 2019 else r.founded - .8, i, str(r.founded), fontsize=7, color=MID, va='center', ha='left' if r.founded < 2019 else 'right')
    ax.set_yticks(range(len(d))); ax.set_yticklabels([f'{a}  {b}' for a, b in zip(d.company, d.company_zh)], fontsize=8.5)
    ax.invert_yaxis(); ax.set_xlim(1984, 2026); clean(ax, left=False); ax.set_ylim(len(d) - .4, -.8)
    ax.set_title(cn, fontsize=12, loc='left', color=colr, weight='bold'); ax.xaxis.grid(color='#F2F2F2', lw=.6); ax.set_axisbelow(True)
    ax.set_xticks([1990, 2000, 2010, 2020])
fig.legend([Line2D([], [], marker=MK[s], ls='', color=MID, ms=7) for s in SEG], SEG, loc='lower center', ncol=6, frameon=False, fontsize=8.5, bbox_to_anchor=(.5, .055))
title(fig, 'Who builds what', 'Selected companies headquartered in each cluster, by founding year. The newest wave, from 2015 on, is robots, chips and models.', y=.965)
fig.text(.05, .02, 'Curated list for illustration, not a ranking or a complete census; segments simplified. Sources: company websites and Wikipedia. Not investment advice.',
         fontsize=7, color=MID)
plt.subplots_adjust(left=.13, right=.98, top=.85, bottom=.16)
fig.savefig('out/assets/companies_by_cluster.png', facecolor=PAPER); plt.close(fig)

# ------------------------------------------------------------------ 6. scatter-plot matrix across the 31 provinces
V = [('gdp_per_capita_cny_2025', 'GDP per person\n2025 (k yuan, log)', lambda x: np.log10(x / 1e3)),
     ('rd_intensity_pct_2024', 'R&D, % of GDP\n2024', lambda x: x),
     ('rd_spending_cny_100m_2024', 'R&D spending\n2024 (100m yuan, log)', lambda x: np.log10(x)),
     ('gdp_nominal_cagr_2020_2025_pct', 'Nominal GDP growth\n2020 to 2025 (%/yr)', lambda x: x)]
X = pd.DataFrame({k: f(pv[k]) for k, _, f in V}); isc = pv.cluster.notna().values
TK = {0: [50, 100, 200], 2: [10, 100, 1000, 5000]}
n = len(V)
fig, axs = plt.subplots(n, n, figsize=(11, 11))
for i in range(n):
    for j in range(n):
        ax = axs[i, j]; xi, yj = X.iloc[:, j], X.iloc[:, i]
        if i == j:
            ax.hist(xi, bins=10, color=LIGHT, ec=PAPER); ax.set_yticks([])
            for v in xi[isc]: ax.axvline(v, color=RED, lw=1)
        else:
            ax.scatter(xi[~isc], yj[~isc], s=16, c=BLUE_SOFT, ec=BLUE, lw=.5)
            ax.scatter(xi[isc], yj[isc], s=34, c=RED, ec=PAPER, lw=.6, zorder=3)
            r = np.corrcoef(xi, yj)[0, 1]
            ax.text(.04, .92, f'r = {r:.2f}', transform=ax.transAxes, fontsize=7.5, color=MID)
            if i == 1 and j == 0:
                for k in np.where(isc)[0]: ax.annotate(pv.province[k], (xi[k], yj[k]), xytext=(-5, 3) if pv.province[k] == 'Beijing' else (4, 3), ha='right' if pv.province[k] == 'Beijing' else 'left', textcoords='offset points', fontsize=7, color=RED)
        for s_ in ('top', 'right'): ax.spines[s_].set_visible(False)
        ax.tick_params(labelsize=7, length=2)
        if j in TK: ax.set_xticks(np.log10(TK[j])); ax.set_xticklabels(TK[j])
        if i in TK and i != j: ax.set_yticks(np.log10(TK[i])); ax.set_yticklabels(TK[i])
        if i < n - 1: ax.set_xticklabels([])
        if j > 0 and i != j: ax.set_yticklabels([])
        if i == n - 1: ax.set_xlabel(V[j][1], fontsize=8.5)
        if j == 0: ax.set_ylabel(V[i][1], fontsize=8.5)
title(fig, 'Rich provinces spend more on research', 'Scatter-plot matrix of the 31 provinces. Red: Beijing, Guangdong and Zhejiang. r is the Pearson correlation on the plotted scale.', y=.965)
fig.text(.05, .015, 'Data: NBS (R&D 2024), provincial GDP from NBS via Wikipedia. Correlation, not causation; 31 points only.', fontsize=7, color=MID)
plt.subplots_adjust(left=.1, right=.97, top=.89, bottom=.08, hspace=.12, wspace=.12)
fig.savefig('out/assets/scatter_matrix_provinces.png', facecolor=PAPER); plt.close(fig)
print(sorted(os.listdir('out/assets')))
