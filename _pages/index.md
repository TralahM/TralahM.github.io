# Extracting Structured Data From Wikipedia

## Extracting Structured Data from Unstructured Wikipedia Sites.

This project we develop a tool to extract structured wikipedia tables as
*csv* or *json* given a wikipedia website link.

Useful for data mining.

``` python
#!/usr/bin/env python
# echo:true
#"""Wikipedia tables extractor."""
from bs4 import BeautifulSoup
import requests
import itertools
import pandas as pd
import numpy as np
import re
import sys
import argparse
```

``` python
def remove_bracs_parens(string, include_parens=False):
    if include_parens:
        return re.sub(r"\n|(\s+){2,20}|\[.*\]", "", string)
    return re.sub(r"\n|(\s+){2,20}|\(.*\)|\[.*\]", "", string)



def remove_wiki_refs(string):
    return re.sub(r"\[(\d+)\]|\[(\w+)\]", "", string)

_float_regexp = re.compile(
    r"^[-+]?(?:\b[0-9]+(?:\.[0-9]*)?|\.[0-9]+\b)(?:[eE][-+]?[0-9]+\b)?$"
).match


def is_float_re(str):
    return True if _float_regexp(str) else False

```

``` python
# echo:true
def get_tables(wikipedia_url):
    """Use BeautifulSoup to get a list of table elements of class wikitable."""
    wikipedia_url = wikipedia_url
    page = requests.get(wikipedia_url)
    soup = BeautifulSoup(page.content, "lxml")
    tables = soup.find_all("table", {"class", "table"})  # or wikitable
    wiki_tables = soup.find_all("table", {"class": "wikitable"})
    tables = wiki_tables if len(wiki_tables) > 0 else tables
    # table = tables[table_from_top - 1]
    return tables
```

``` python
def get_feature_name(header, include_parens=True):
    feature_name = "".join(header.find_all(string=True))
    feature_name.replace(r"\n", " ")
    lspaces = sum(1 for _ in itertools.takewhile(str.isspace, feature_name))
    feature_name = feature_name[lspaces:]
    feature_name = remove_bracs_parens(feature_name, include_parens)
    feature_name = remove_wiki_refs(feature_name)
    return feature_name.strip()

```

``` python

def all_same(iterable):
    if len(iterable) > 0:
        return all([x == iterable[0] for x in iterable])
    else:
        return False

def remove_duplicates(iterable):
    after = []
    for i in iterable:
        if i not in after:
            after.append(i)
        else:
            after.append("")
    return tuple(after)


```

``` python
from typing import List

class TH:
    def __init__(
        self,
        text: str,
        index: int,
        level: int = 0,
        rowspan: int = 1,
        colspan: int = 1,
        parent=None,
    ):
        self.text = text
        self.index = index
        self.level = level
        self.rowspan = rowspan
        self.colspan = colspan
        self.parent = parent
        self.children: List[TH] = []
        self.rowspan_child = None
        if self.rowspan > 1:
            self.set_rowspan_child(
                TH(
                    self.text,
                    self.index,
                    level + 1,
                    self.rowspan - 1,
                    self.colspan,
                )
            )
        if parent is not None:
            parent.add_child(self)

    def set_rowspan_child(self, child):
        self.rowspan_child = child

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def set_parent(self, parent):
        self.parent = parent

    @property
    def expanded(self):
        return [
            TH(
                self.text,
                self.index + i,
                self.level,
                self.rowspan,
                1,
                self.parent,
            )
            for i in range(self.colspan)
        ]

    def __repr__(self):
        return self.text


class LevelRow:
    def __init__(self, level, children: List[TH]):
        self.level = level
        self.children: List[TH] = children

    @property
    def expanded(self):
        expanded = []
        for child in self.children:
            expanded.extend(child.expanded)
        return expanded

    def expanded_text(self):
        return [child.text for child in self.expanded]

    def rowspan_exists_at(self, index):
        if index >= len(self.children):
            return False
        return self.expanded[index].rowspan > 1

    def get_rowspan_at(self, index):
        return self.expanded[index].rowspan_child


```

``` python
class WikiTableParser:
    def __init__(self, table_soup):
        self.table_soup = table_soup
        self.all_rows = self.table_soup.find_all("tr")
        self.num_rows = len(self.all_rows)
        self.header_rows = self.find_header_rows()
        self.num_hrows = len(self.header_rows)
        self.per_level_headers = {i: None for i in range(self.num_hrows)}
        self.num_data_rows = self.num_rows - self.num_hrows
        self.feature_tuples = self.get_feature_tuples()
        self.num_cols = len(self.feature_tuples)
        self.feature_names = self.get_feature_names()
        self.table_values = self.get_table_values()
        self.table_data = self.get_table_data()
        # self.feature_types = self.get_feature_types()

    @property
    def has_defined_thead(self):
        return self.table_soup.find("thead") is not None

    @property
    def shape(self):
        return (self.num_data_rows, self.num_cols)

    @property
    def table_caption(self):
        caption = self.table_soup.find("caption")
        if caption is not None:
            return caption.text.strip()
        else:
            return None

    def find_header_rows(self):
        rows_until_first_td = []
        for row in self.all_rows:
            if row.find("td") is not None:
                break
            elif row.find("th") is not None:
                rows_until_first_td.append(row)
        return rows_until_first_td

    def get_feature_tuples(self):
        self.process_headers()
        headers = []
        for i in range(self.num_hrows):
            headers.append(self.per_level_headers[i].expanded_text())
        return list(zip(*headers))

    def get_feature_names(self):
        return [remove_duplicates(t) for t in self.feature_tuples]

    @property
    def get_table_headers(self):
        """Return a list of feature_names or the headers of a table."""
        return self.feature_names

    def get_table_data(self):
        """Get Table Data.

        Returns a list of dict objects key value pairs of
        [{feature_name[i] :feature_value[i],...},...].
        """
        samples = []
        feature_names = self.feature_names
        sample_rows = self.table_values
        for features in sample_rows:
            samples.append(dict(zip(feature_names, features)))
        return samples

    def get_table_values(self):
        """Return the Feature values of a table element."""
        values = []
        sample_rows = self.table_soup.find_all("tr")
        for sample_row in sample_rows:
            features = []
            for feature_col in sample_row.find_all("td"):
                n_spans = int(feature_col.attrs.get("colspan", 1))
                text = get_feature_name(feature_col, include_parens=False)
                if "," in text:
                    x = text.replace(",", "").replace(" ", "")
                    if x.isnumeric() or x.isdecimal() or x.isdigit() or is_float_re(x):
                        [features.append(x) for _ in range(n_spans)]
                    else:
                        [features.append(f"'{text}'") for _ in range(n_spans)]
                else:
                    [features.append(text) for _ in range(n_spans)]
            if len(features) > 0:
                values.append(features)
        return values

    def process_headers(self):
        for level, header_row in enumerate(self.header_rows):
            level_headers = []
            for header in header_row.find_all("th"):
                feature_name = get_feature_name(header)
                rowspan = int(header.attrs.get("rowspan", 1))
                colspan = int(header.attrs.get("colspan", 1))
                index = sum([lh.colspan for lh in level_headers])
                if level > 0:
                    prev_lh = self.per_level_headers[level - 1]
                    prev_expanded = prev_lh.expanded
                    while prev_lh.rowspan_exists_at(index):
                        level_headers.append(prev_lh.get_rowspan_at(index))
                        index += 1
                    parent = (
                        prev_expanded[index] if index < len(
                            prev_expanded) else None
                    )
                    th = TH(feature_name, index, level,
                            rowspan, colspan, parent)
                    level_headers.extend(th.expanded)
                    findex = th.expanded[-1].index + 1
                    while prev_lh.rowspan_exists_at(findex):
                        level_headers.append(prev_lh.get_rowspan_at(findex))
                        findex += 1
                else:
                    th = TH(feature_name, index, level, rowspan, colspan, None)
                    level_headers.extend(th.expanded)
            self.per_level_headers[level] = LevelRow(level, level_headers)

    @property
    def as_pandas_df(self, with_headers=True):
        if not with_headers:
            return pd.DataFrame(self.table_values).dropna(axis=0, how="all")
        df = pd.DataFrame(self.table_data).dropna(axis=0, how="all")
        columns = df.columns
        tup_cols = [c for c in columns if isinstance(c, tuple)]
        if len(tup_cols) == 0:
            return df
        if len(tup_cols) == len(columns):
            df.columns = pd.MultiIndex.from_tuples(tup_cols)
        return df

    def print_headers_debug(self):
        for i in range(self.num_hrows):
            lh = self.per_level_headers[i]
            row = lh.expanded_text()
            print(row, "len:", len(row))


```

``` python
def print_table_headers(table_headers):
    """Print a formatted table feature_names or headers."""
    print(
        ",".join([str(i) for i in table_headers])
        .replace("\n", "")
        .replace(" ,", ",")
        .replace("  ", " ")
    )

def print_table_values(table_values):
    """Print a formatted table feature_values or rows."""
    for row in table_values[:5]:
        print(",".join([i if i else "" for i in row]).replace("\n", ""))


def list_page_tables(tables):
    """Print all headers of all tables in tables."""
    ps=[]
    for i, table in enumerate(tables):
        print(f"\n{'==='*13}> Table {i+1}")
        ps_table = WikiTableParser(table)
        print("table caption: ", ps_table.table_caption)
        print_table_headers(ps_table.get_table_headers)
        print_table_values(ps_table.table_values)
        ps_table.print_headers_debug()
        print("===" * 13)
        ps.append(ps_table)
    return ps
```

``` python

def save_to_json(df, filename):
    """Save the pd.DataFrame to a CSV file with the given filename."""
    return df.to_json(filename, index=False, orient="records")


def save_to_csv(df, filename):
    """Save the pd.DataFrame to a CSV file with the given filename."""
    return df.to_csv(filename, index=False)


def get_filename_from_wikipedia_url(url, ext=".csv"):
    """Get filename from wikipedia_url."""
    return url.split("/")[-1] + ext
```

``` python
def run_table_extraction(
    wikipedia_url,
    save_to_csv=False,
    save_all=False,
    save_to_json=False,
    save_all_json=False,
    table_number=1,
    outf=None,
    exclude_column=None,
    **kwargs,
):
    args = argparse.Namespace(
        wikipedia_url=wikipedia_url,
        save_to_csv=save_to_csv,
        save_all=save_all,
        save_to_json=save_to_json,
        save_all_json=save_all_json,
        N=table_number,
        outf=outf,
        exclude_col=exclude_column,
    )
    tables = get_tables(args.wikipedia_url)
    ps_tables = [WikiTableParser(table) for table in tables]
    if not len(tables):
        print("0 Tables Found!\tExiting...")
        sys.exit(0)
    if args.save_all:
        if not args.outf:
            filename = get_filename_from_wikipedia_url(args.wikipedia_url)
        else:
            filename = args.outf
        for i in range(len(tables)):
            table = ps_tables[i]
            df = table.as_pandas_df
            cols = df.columns
            if args.exclude_col:
                col = cols[args.exclude_col - 1]
                cols = [c for c in cols if c != col]
            save_to_csv(df[cols], filename[:-4] + str(i) + ".csv")
    if args.save_all_json:
        if not args.outf:
            filename = get_filename_from_wikipedia_url(
                args.wikipedia_url,
                ext=".json",
            )
        else:
            filename = args.outf
        for i in range(len(tables)):
            table = ps_tables[i]
            df = table.as_pandas_df
            cols = df.columns
            if args.exclude_col:
                col = cols[args.exclude_col - 1]
                cols = [c for c in cols if c != col]
            save_to_json(df[cols], filename[:-4] + str(i) + ".json")
    if args.save_to_csv:
        N = int(args.N)
        table = ps_tables[N - 1]
        if not args.outf:
            filename = get_filename_from_wikipedia_url(args.wikipedia_url)
        else:
            filename = args.outf
        df = table.as_pandas_df
        cols = df.columns
        if args.exclude_col:
            col = cols[args.exclude_col - 1]
            cols = [c for c in cols if c != col]
        save_to_csv(df[cols], filename)
    else:
        filename = get_filename_from_wikipedia_url(args.wikipedia_url)
        list_page_tables(tables)
        print("\n")
        print(f"Default Output Filename: {filename}")
        dfs = []
        for i in range(len(tables)):
            table = ps_tables[i]
            df = table.as_pandas_df
            cols = df.columns
            if args.exclude_col:
                col = cols[args.exclude_col - 1]
                cols = [c for c in cols if c != col]
            dfs.append(df[cols])
        return dfs,ps_tables
    return [p.as_pandas_df for p in ps_tables], ps_tables

```

## Testing

``` python
# echo:true
dfs,ts = run_table_extraction(
    wikipedia_url="https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)",
    save_to_csv=False,
    save_all=False,
    save_to_json=False,
    save_all_json=False,
    table_number=1,
    outf=None,
    exclude_column=None,
)

df=dfs[0]
lcs=list(df.columns)[1:]
yrs=[l for l in lcs if l[1]=='Year']
vals=[x for x in lcs if x not in yrs]
df[vals]=df[vals].replace({"—":np.nan,})
```


    =======================================> Table 1
    table caption:  GDP (million US$) by country
    ('Country/Territory', ''),('IMF', 'Forecast'),('IMF', 'Year'),('World Bank', 'Estimate'),('World Bank', 'Year'),('United Nations', 'Estimate'),('United Nations', 'Year')
    World,109529216,2024,105435540,2023,100834796,2022
    United States,28781083,2024,27360935,2023,25744100,2022
    China,18532633,2024,17794782,2023,17963170,2022
    Germany,4591100,2024,4456081,2023,4076923,2022
    Japan,4110452,2024,4212945,2023,4232173,2022
    ['Country/Territory', 'IMF', 'IMF', 'World Bank', 'World Bank', 'United Nations', 'United Nations'] len: 7
    ['Country/Territory', 'Forecast', 'Year', 'Estimate', 'Year', 'Estimate', 'Year'] len: 7
    =======================================


    Default Output Filename: List_of_countries_by_GDP_(nominal).csv

``` python
# echo:true
df.shape
```

    (210, 7)

**Nominal GDP in (million US\$)**

``` python
df = df.astype({('IMF','Year'):str,('World Bank', 'Year'):str,('United Nations', 'Year'):str})
df = df.astype({t:np.float32 for t in vals})
df.dtypes
df.describe(include=["object"])
df.describe()
```

    Country/Territory               object
    IMF                Forecast    float32
                       Year         object
    World Bank         Estimate    float32
                       Year         object
    United Nations     Estimate    float32
                       Year         object
    dtype: object

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead tr th {
        text-align: left;
    }
</style>

|        | Country/Territory | IMF  | World Bank | United Nations |
|--------|-------------------|------|------------|----------------|
|        |                   | Year | Year       | Year           |
| count  | 210               | 210  | 210        | 210            |
| unique | 210               | 4    | 4          | 2              |
| top    | World             | 2024 | 2023       | 2022           |
| freq   | 1                 | 190  | 186        | 209            |

</div>
<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead tr th {
        text-align: left;
    }
</style>

|       | IMF            | World Bank     | United Nations |
|-------|----------------|----------------|----------------|
|       | Forecast       | Estimate       | Estimate       |
| count | 195.00         | 202.00         | 209.00         |
| mean  | 1,123,227.75   | 1,037,206.12   | 961,269.88     |
| std   | 8,200,460.50   | 7,751,885.00   | 7,293,077.00   |
| min   | 66.00          | 62.00          | 59.00          |
| 25%   | 13,276.00      | 9,284.00       | 8,772.00       |
| 50%   | 46,790.00      | 37,573.00      | 31,717.00      |
| 75%   | 297,844.50     | 259,432.25     | 237,101.00     |
| max   | 109,529,216.00 | 105,435,536.00 | 100,834,800.00 |

</div>

### GDP (million US\$) by country

#### Top 10

``` python
# echo:true
df.head(10)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead tr th {
        text-align: left;
    }
</style>

|     | Country/Territory | IMF            |      | World Bank     |      | United Nations |      |
|-----|-------------------|----------------|------|----------------|------|----------------|------|
|     |                   | Forecast       | Year | Estimate       | Year | Estimate       | Year |
| 0   | World             | 109,529,216.00 | 2024 | 105,435,536.00 | 2023 | 100,834,800.00 | 2022 |
| 1   | United States     | 28,781,084.00  | 2024 | 27,360,936.00  | 2023 | 25,744,100.00  | 2022 |
| 2   | China             | 18,532,632.00  | 2024 | 17,794,782.00  | 2023 | 17,963,170.00  | 2022 |
| 3   | Germany           | 4,591,100.00   | 2024 | 4,456,081.00   | 2023 | 4,076,923.00   | 2022 |
| 4   | Japan             | 4,110,452.00   | 2024 | 4,212,945.00   | 2023 | 4,232,173.00   | 2022 |
| 5   | India             | 3,937,011.00   | 2024 | 3,549,919.00   | 2023 | 3,465,541.00   | 2022 |
| 6   | United Kingdom    | 3,495,261.00   | 2024 | 3,340,032.00   | 2023 | 3,089,072.00   | 2022 |
| 7   | France            | 3,130,014.00   | 2024 | 3,030,904.00   | 2023 | 2,775,316.00   | 2022 |
| 8   | Brazil            | 2,331,391.00   | 2024 | 2,173,666.00   | 2023 | 1,920,095.00   | 2022 |
| 9   | Italy             | 2,328,028.00   | 2024 | 2,254,851.00   | 2023 | 2,046,952.00   | 2022 |

</div>

### GDP (million US\$) by country

#### Bottom 10

``` python
# echo:true
df.tail(10)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead tr th {
        text-align: left;
    }
</style>

|     | Country/Territory     | IMF      |      | World Bank |      | United Nations |      |
|-----|-----------------------|----------|------|------------|------|----------------|------|
|     |                       | Forecast | Year | Estimate   | Year | Estimate       | Year |
| 200 | Samoa                 | 1,024.00 | 2024 | 934.00     | 2023 | 857.00         | 2022 |
| 201 | São Tomé and Príncipe | 751.00   | 2024 | 603.00     | 2023 | 546.00         | 2022 |
| 202 | Dominica              | 708.00   | 2024 | 654.00     | 2023 | 612.00         | 2022 |
| 203 | Tonga                 | 581.00   | 2024 | 500.00     | 2022 | 488.00         | 2022 |
| 204 | Micronesia            | 484.00   | 2024 | 460.00     | 2023 | 427.00         | 2022 |
| 205 | Kiribati              | 311.00   | 2024 | 279.00     | 2023 | 223.00         | 2022 |
| 206 | Palau                 | 308.00   | 2024 | 263.00     | 2023 | 225.00         | 2022 |
| 207 | Marshall Islands      | 305.00   | 2024 | 284.00     | 2023 | 279.00         | 2022 |
| 208 | Nauru                 | 161.00   | 2024 | 154.00     | 2023 | 147.00         | 2022 |
| 209 | Tuvalu                | 66.00    | 2024 | 62.00      | 2023 | 59.00          | 2022 |

</div>

``` python
# echo:true
df[df['Country/Territory']=='Kenya']
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead tr th {
        text-align: left;
    }
</style>

|     | Country/Territory | IMF        |      | World Bank |      | United Nations |      |
|-----|-------------------|------------|------|------------|------|----------------|------|
|     |                   | Forecast   | Year | Estimate   | Year | Estimate       | Year |
| 70  | Kenya             | 104,001.00 | 2024 | 107,441.00 | 2023 | 113,419.00     | 2022 |

</div>

**Nominal GDP Per Capita in USD**

``` python
dfs2,ts2=run_table_extraction(
    wikipedia_url="https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)_per_capita",
    save_to_csv=False,
    save_all=False,
    save_to_json=False,
    save_all_json=False,
    table_number=1,
    outf=None,
    exclude_column=None,
)
#len(dfs2)
df2=dfs2[0]
lcs2=list(df2.columns)[1:]
yrs2=[l for l in lcs2 if l[1]=='Year']
vals2=[x for x in lcs2 if x not in yrs2]
df2[vals2]=df2[vals2].replace({"—":np.nan,})
```


    =======================================> Table 1
    table caption:  GDP (in USD) per capita by country, territory, non-sovereign state or non-IMF member
    ('Country/Territory', ''),('IMF', 'Estimate'),('IMF', 'Year'),('World Bank', 'Estimate'),('World Bank', 'Year'),('United Nations', 'Estimate'),('United Nations', 'Year')
    Monaco,—,—,240862,2022,234317,2021
    Liechtenstein,—,—,187267,2022,169260,2021
    Luxembourg,131384,2024,128259,2023,133745,2021
    Bermuda,—,—,123091,2022,112653,2021
    Ireland,106059,2024,103685,2023,101109,2021
    ['Country/Territory', 'IMF', 'IMF', 'World Bank', 'World Bank', 'United Nations', 'United Nations'] len: 7
    ['Country/Territory', 'Estimate', 'Year', 'Estimate', 'Year', 'Estimate', 'Year'] len: 7
    =======================================


    Default Output Filename: List_of_countries_by_GDP_(nominal)_per_capita.csv

``` python
# echo:true
df2.shape
```

    (222, 7)

``` python
df2 = df2.astype({t:np.float32 for t in vals2})
df2 = df2.astype({t:str for t in yrs2})
df2.dtypes
df2.describe(include=["object"])
df2.describe()
```

    Country/Territory               object
    IMF                Estimate    float32
                       Year         object
    World Bank         Estimate    float32
                       Year         object
    United Nations     Estimate    float32
                       Year         object
    dtype: object

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead tr th {
        text-align: left;
    }
</style>

|        | Country/Territory | IMF  | World Bank | United Nations |
|--------|-------------------|------|------------|----------------|
|        |                   | Year | Year       | Year           |
| count  | 222               | 222  | 222        | 222            |
| unique | 222               | 4    | 8          | 3              |
| top    | Monaco            | 2024 | 2023       | 2021           |
| freq   | 1                 | 190  | 188        | 212            |

</div>
<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead tr th {
        text-align: left;
    }
</style>

|       | IMF        | World Bank | United Nations |
|-------|------------|------------|----------------|
|       | Estimate   | Estimate   | Estimate       |
| count | 195.00     | 216.00     | 213.00         |
| mean  | 18,333.29  | 21,421.44  | 18,584.14      |
| std   | 23,901.34  | 31,290.97  | 29,127.32      |
| min   | 230.00     | 200.00     | 302.00         |
| 25%   | 2,579.00   | 2,524.00   | 2,306.00       |
| 50%   | 7,327.00   | 8,257.00   | 6,785.00       |
| 75%   | 24,080.00  | 29,269.00  | 21,390.00      |
| max   | 131,384.00 | 240,862.00 | 234,317.00     |

</div>

### GDP (in USD) per capita by country, territory, non-sovereign state or non-IMF member

#### Top 10

``` python
# echo:true
df2.head(10)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead tr th {
        text-align: left;
    }
</style>

|     | Country/Territory | IMF        |      | World Bank |      | United Nations |      |
|-----|-------------------|------------|------|------------|------|----------------|------|
|     |                   | Estimate   | Year | Estimate   | Year | Estimate       | Year |
| 0   | Monaco            | NaN        | —    | 240,862.00 | 2022 | 234,317.00     | 2021 |
| 1   | Liechtenstein     | NaN        | —    | 187,267.00 | 2022 | 169,260.00     | 2021 |
| 2   | Luxembourg        | 131,384.00 | 2024 | 128,259.00 | 2023 | 133,745.00     | 2021 |
| 3   | Bermuda           | NaN        | —    | 123,091.00 | 2022 | 112,653.00     | 2021 |
| 4   | Ireland           | 106,059.00 | 2024 | 103,685.00 | 2023 | 101,109.00     | 2021 |
| 5   | Switzerland       | 105,669.00 | 2024 | 99,995.00  | 2023 | 93,525.00      | 2021 |
| 6   | Cayman Islands    | NaN        | —    | 96,074.00  | 2022 | 85,250.00      | 2021 |
| 7   | Norway            | 94,660.00  | 2024 | 87,962.00  | 2023 | 89,242.00      | 2021 |
| 8   | Isle of Man       | NaN        | —    | 94,124.00  | 2021 | NaN            | —    |
| 9   | Singapore         | 88,447.00  | 2024 | 84,734.00  | 2023 | 66,822.00      | 2021 |

</div>

### GDP (in USD) per capita by country, territory, non-sovereign state or non-IMF member

#### Bottom 10

``` python
# echo:true
df2.tail(10)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead tr th {
        text-align: left;
    }
</style>

|     | Country/Territory        | IMF      |      | World Bank |      | United Nations |      |
|-----|--------------------------|----------|------|------------|------|----------------|------|
|     |                          | Estimate | Year | Estimate   | Year | Estimate       | Year |
| 212 | Sudan                    | 547.00   | 2024 | 2,272.00   | 2023 | 786.00         | 2021 |
| 213 | Madagascar               | 538.00   | 2024 | 529.00     | 2023 | 500.00         | 2021 |
| 214 | Central African Republic | 538.00   | 2024 | 445.00     | 2023 | 461.00         | 2021 |
| 215 | Sierra Leone             | 527.00   | 2024 | 433.00     | 2023 | 505.00         | 2021 |
| 216 | Yemen                    | 486.00   | 2024 | 533.00     | 2023 | 302.00         | 2021 |
| 217 | Malawi                   | 481.00   | 2024 | 673.00     | 2023 | 613.00         | 2021 |
| 218 | South Sudan              | 422.00   | 2024 | 1,072.00   | 2015 | 400.00         | 2021 |
| 219 | Afghanistan              | 422.00   | 2022 | 353.00     | 2022 | 373.00         | 2021 |
| 220 | Syria                    | NaN      | —    | 421.00     | 2021 | 925.00         | 2021 |
| 221 | Burundi                  | 230.00   | 2024 | 200.00     | 2023 | 311.00         | 2021 |

</div>

``` python
# echo:true
df2[df2['Country/Territory']=='Kenya']
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead tr th {
        text-align: left;
    }
</style>

|     | Country/Territory | IMF      |      | World Bank |      | United Nations |      |
|-----|-------------------|----------|------|------------|------|----------------|------|
|     |                   | Estimate | Year | Estimate   | Year | Estimate       | Year |
| 177 | Kenya             | 1,983.00 | 2024 | 1,950.00   | 2023 | 2,082.00       | 2021 |

</div>

``` python
# echo:true
df2[df2['Country/Territory']=='United States']
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead tr th {
        text-align: left;
    }
</style>

|     | Country/Territory | IMF       |      | World Bank |      | United Nations |      |
|-----|-------------------|-----------|------|------------|------|----------------|------|
|     |                   | Estimate  | Year | Estimate   | Year | Estimate       | Year |
| 10  | United States     | 85,373.00 | 2024 | 81,695.00  | 2023 | 69,185.00      | 2021 |

</div>

## List of countries by minimum wage

``` python
# echo:true
dfs3,ts3 = run_table_extraction(
    wikipedia_url="https://en.wikipedia.org/wiki/List_of_countries_by_minimum_wage",
)
dfa=dfs3[0]
dfb=dfs3[1]
```


    =======================================> Table 1
    table caption:  Minimum wages by country. USD and Int$ PPP.
    ('Country', ''),('Minimum wage', ''),('Annual', 'Nominal (US$)'),('Annual', 'PPP (Int$)'),('Workweek (hours)', ''),('Hourly', 'Nominal (US$)'),('Hourly', 'PPP (Int$)'),('Percent of GDP per capita', ''),('Effective per', '')
    Afghanistan,'؋5,500 . There was no minimum wage for permanent workers in the private sector.',858,3272,40,0.41,1.57,168.3%,2017
    Albania,'L40,000 . The law establishes a 40-hour workweek, but the actual workweek is typically set by individual or collective-bargaining agreement.',4637,8697,40,2.23,4.18,75.4%,1 Apr 2023
    Algeria,'د.ج 20,000 .',1777,6247,40,0.85,3,41.6%,1 May 2020
    Andorra,€7.42  hourly.,18253,13493,40,8,6,28%,1 Jan 2023
    Angola,'Kz 32,181',663,3161,44,0.29,1.38,49%,2022
    ['Country', 'Minimum wage', 'Annual', 'Annual', 'Workweek (hours)', 'Hourly', 'Hourly', 'Percent of GDP per capita', 'Effective per'] len: 9
    ['Country', 'Minimum wage', 'Nominal (US$)', 'PPP (Int$)', 'Workweek (hours)', 'Nominal (US$)', 'PPP (Int$)', 'Percent of GDP per capita', 'Effective per'] len: 9
    =======================================

    =======================================> Table 2
    table caption:  OECD Real minimum wages (US dollar)[256]
    ('Country', '', ''),('2018', 'Nominal', 'Annual'),('2018', 'Nominal', 'Hourly'),('2018', 'PPP', 'Annual'),('2018', 'PPP', 'Hourly'),('2018', 'Annual workinghours', ''),('2019', 'Nominal', 'Annual'),('2019', 'Nominal', 'Hourly'),('2019', 'PPP', 'Annual'),('2019', 'PPP', 'Hourly'),('2019', 'Annual workinghours', '')
    Australia,25970.8,13.1,24481.2,12.4,1976,26388.5,13.4,24874.9,12.6,1976
    Belgium,21293.0,10.2,22746.8,10.9,2086,21410.8,10.3,22872.6,11.0,2086
    Canada,20552.5,9.9,20946.0,10.1,2080,20880.7,10.0,21280.5,10.2,2080
    Chile,4902.5,2.1,7044.4,3.0,2346,5101.7,2.2,7330.7,3.1,2346
    Colombia,3451.3,1.2,7677.4,2.6,2920,3533.7,1.2,7860.9,2.7,2920
    ['Country', '2018', '2018', '2018', '2018', '2018', '2019', '2019', '2019', '2019', '2019'] len: 11
    ['Country', 'Nominal', 'Nominal', 'PPP', 'PPP', 'Annual workinghours', 'Nominal', 'Nominal', 'PPP', 'PPP', 'Annual workinghours'] len: 11
    ['Country', 'Annual', 'Hourly', 'Annual', 'Hourly', 'Annual workinghours', 'Annual', 'Hourly', 'Annual', 'Hourly', 'Annual workinghours'] len: 11
    =======================================


    Default Output Filename: List_of_countries_by_minimum_wage.csv

``` python
# echo:true
dfa.shape
dfa.dtypes
dfa.describe()
```

    (201, 9)

    Country                                     object
    Minimum wage                                object
    Annual                     Nominal (US$)    object
                               PPP (Int$)       object
    Workweek (hours)                            object
    Hourly                     Nominal (US$)    object
                               PPP (Int$)       object
    Percent of GDP per capita                   object
    Effective per                               object
    dtype: object

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead tr th {
        text-align: left;
    }
</style>

|        | Country     | Minimum wage | Annual         |             | Workweek (hours) | Hourly         |             | Percent of GDP per capita | Effective per |
|--------|-------------|--------------|----------------|-------------|------------------|----------------|-------------|---------------------------|---------------|
|        |             |              | Nominal (US\$) | PPP (Int\$) |                  | Nominal (US\$) | PPP (Int\$) |                           |               |
| count  | 201         | 201          | 201            | 201         | 200              | 200            | 200         | 200                       | 200           |
| unique | 201         | 196          | 160            | 157         | 14               | 135            | 142         | 151                       | 88            |
| top    | Afghanistan | None.        |                |             | 40               |                |             |                           | 2017          |
| freq   | 1           | 4            | 42             | 45          | 103              | 42             | 45          | 44                        | 20            |

</div>

``` python
# echo:true
dfa.head(10)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead tr th {
        text-align: left;
    }
</style>

|     | Country             | Minimum wage                                      | Annual         |             | Workweek (hours) | Hourly         |             | Percent of GDP per capita | Effective per    |
|-----|---------------------|---------------------------------------------------|----------------|-------------|------------------|----------------|-------------|---------------------------|------------------|
|     |                     |                                                   | Nominal (US\$) | PPP (Int\$) |                  | Nominal (US\$) | PPP (Int\$) |                           |                  |
| 0   | Afghanistan         | '؋5,500 . There was no minimum wage for perman... | 858            | 3272        | 40               | 0.41           | 1.57        | 168.3%                    | 2017             |
| 1   | Albania             | 'L40,000 . The law establishes a 40-hour workw... | 4637           | 8697        | 40               | 2.23           | 4.18        | 75.4%                     | 1 Apr 2023       |
| 2   | Algeria             | 'د.ج 20,000 .'                                    | 1777           | 6247        | 40               | 0.85           | 3           | 41.6%                     | 1 May 2020       |
| 3   | Andorra             | €7.42 hourly.                                     | 18253          | 13493       | 40               | 8              | 6           | 28%                       | 1 Jan 2023       |
| 4   | Angola              | 'Kz 32,181'                                       | 663            | 3161        | 44               | 0.29           | 1.38        | 49%                       | 2022             |
| 5   | Antigua and Barbuda | EC\$8.2 per hour .                                | 6317           | 7788        | 40               | 3.04           | 3.74        | 34.4%                     | 1 Nov 2014       |
| 6   | Argentina           | 'AR\$268,056 .'                                   | 36685          | 322362      | 48               | 14.7           | 129.15      | '1,616.7%'                | 1 September 2024 |
| 7   | Armenia             | '֏ 75,000 per month.'                             | 1787           | 4567        | 40               | 0.86           | 2.2         | 51.7%                     | 15 Nov 2022      |
| 8   | Australia           | 'Most workers are covered by an award, which m... | 35810          | 29767       | 38               | 18.12          | 15.06       | 64.7%                     | 1 July 2024      |
| 9   | Austria             | 'None: National collective bargaining agreemen... |                |             | 40               |                |             |                           | 2017             |

</div>

``` python
# echo:true
dfb.shape
dfb.dtypes
dfb.describe()
```

    (32, 11)

    Country                                 object
    2018     Nominal              Annual    object
                                  Hourly    object
             PPP                  Annual    object
                                  Hourly    object
             Annual workinghours            object
    2019     Nominal              Annual    object
                                  Hourly    object
             PPP                  Annual    object
                                  Hourly    object
             Annual workinghours            object
    dtype: object

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead tr th {
        text-align: left;
    }
</style>

|        | Country   | 2018    |        |         |        |                     | 2019    |        |         |        |                     |
|--------|-----------|---------|--------|---------|--------|---------------------|---------|--------|---------|--------|---------------------|
|        |           | Nominal |        | PPP     |        | Annual workinghours | Nominal |        | PPP     |        | Annual workinghours |
|        |           | Annual  | Hourly | Annual  | Hourly |                     | Annual  | Hourly | Annual  | Hourly |                     |
| count  | 32        | 32      | 32     | 32      | 32     | 32                  | 32      | 32     | 32      | 32     | 32                  |
| unique | 32        | 32      | 27     | 32      | 29     | 20                  | 32      | 28     | 32      | 27     | 21                  |
| top    | Australia | 25970.8 | 2.8    | 24481.2 | 12.4   | 2086                | 26388.5 | 13.4   | 24874.9 | 11.0   | 2086                |
| freq   | 1         | 1       | 3      | 1       | 2      | 8                   | 1       | 2      | 1       | 3      | 9                   |

</div>

``` python
# echo:true
dfb.head(10)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead tr th {
        text-align: left;
    }
</style>

|     | Country        | 2018    |        |         |        |                     | 2019    |        |         |        |                     |
|-----|----------------|---------|--------|---------|--------|---------------------|---------|--------|---------|--------|---------------------|
|     |                | Nominal |        | PPP     |        | Annual workinghours | Nominal |        | PPP     |        | Annual workinghours |
|     |                | Annual  | Hourly | Annual  | Hourly |                     | Annual  | Hourly | Annual  | Hourly |                     |
| 0   | Australia      | 25970.8 | 13.1   | 24481.2 | 12.4   | 1976                | 26388.5 | 13.4   | 24874.9 | 12.6   | 1976                |
| 1   | Belgium        | 21293.0 | 10.2   | 22746.8 | 10.9   | 2086                | 21410.8 | 10.3   | 22872.6 | 11.0   | 2086                |
| 2   | Canada         | 20552.5 | 9.9    | 20946.0 | 10.1   | 2080                | 20880.7 | 10.0   | 21280.5 | 10.2   | 2080                |
| 3   | Chile          | 4902.5  | 2.1    | 7044.4  | 3.0    | 2346                | 5101.7  | 2.2    | 7330.7  | 3.1    | 2346                |
| 4   | Colombia       | 3451.3  | 1.2    | 7677.4  | 2.6    | 2920                | 3533.7  | 1.2    | 7860.9  | 2.7    | 2920                |
| 5   | Czech Republic | 6565.8  | 3.3    | 10789.9 | 5.4    | 2000                | 7064.3  | 3.5    | 11609.0 | 5.8    | 2000                |
| 6   | Estonia        | 6869.8  | 3.4    | 9890.2  | 4.9    | 2020                | 7254.2  | 3.6    | 10443.5 | 5.2    | 2019                |
| 7   | France         | 20989.7 | 13.2   | 21860.3 | 12.0   | 2289                | 21889.6 | 11.2   | 21949.0 | 12.1   | 2189                |
| 8   | Germany        | 20414.6 | 10.0   | 23439.6 | 11.5   | 2033                | 20916.3 | 10.3   | 24015.6 | 11.8   | 2033                |
| 9   | Greece         | 9208.7  | 3.7    | 13040.0 | 5.2    | 2507                | 10103.7 | 4.0    | 14307.4 | 5.7    | 2507                |

</div>
