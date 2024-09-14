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
def remove_bracs_parens(string):
    return re.sub(r"\n|(\s+){2,20}|\(.*\)|\[.*\]", "", string)


def remove_wiki_refs(string):
    return re.sub(r"\[(\d+)\]|\[(\w+)\]", "", string)
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
def get_feature_name(header):
    feature_name = " ".join(header.find_all(string=True))
    feature_name.replace(r"\n", "")
    lspaces = sum(1 for _ in itertools.takewhile(str.isspace, feature_name))
    feature_name = feature_name[lspaces:]
    feature_name = remove_bracs_parens(feature_name)
    feature_name = remove_wiki_refs(feature_name)
    return feature_name.strip()

```

``` python

def all_same(iterable):
    if len(iterable) > 0:
        return all([x == iterable[0] for x in iterable])
    else:
        return False
```

``` python
def get_table_headers(table):
    """Return a list of feature_names or the headers of a table."""
    feature_names = []
    all_rows = table.find_all("tr")
    rows_until_first_td = []
    for row in all_rows:
        if row.find("td") is not None:
            break
        elif row.find("th") is not None:
            rows_until_first_td.append(row)
    th_parents = rows_until_first_td
    num_headers = len(th_parents)
    if num_headers == 1:
        header_row = table.find("tr")
        for header in header_row.find_all("th"):
            feature_name = " ".join(header.find_all(string=True))
            feature_name.replace(r"\n", "")
            lspaces = sum(
                [
                    1
                    for _ in itertools.takewhile(
                        str.isspace,
                        feature_name,
                    )
                ],
            )
            feature_name = feature_name[lspaces:]
            feature_name = remove_bracs_parens(feature_name)
            feature_name = remove_wiki_refs(feature_name)
            feature_names.append(feature_name.strip())
    else:
        metadata = {
            "rowspan_features": {},
            "colspan_features": [],
            "inorder_features": [],
            "per_row_features": {i: [] for i in range(num_headers)},
        }
        for i, header_row in enumerate(th_parents):
            row_features = []
            for j, header in enumerate(header_row.find_all("th")):
                feature_name = get_feature_name(header)
                metadata[feature_name] = dict(
                    rowspan=int(header.attrs.get("rowspan", 1)),
                    colspan=int(header.attrs.get("colspan", 1)),
                )
                if header.attrs.get("rowspan") is not None:
                    pv_cspans = sum(
                        [
                            metadata[f].get("colspan", 1)
                            for f in metadata["colspan_features"]
                            if f in metadata["per_row_features"][j] and j > 0
                        ],
                    )
                    metadata["rowspan_features"][feature_name] = j + pv_cspans
                if header.attrs.get("colspan") is not None:
                    metadata["colspan_features"].append(feature_name)
                metadata["inorder_features"].append(feature_name)
                row_features.append(feature_name)
            metadata["per_row_features"][i] = row_features
        expanded_colspan_features = {i: [] for i in range(num_headers)}
        # print(metadata)
        for i, features in metadata["per_row_features"].items():
            expanded = []
            for feature in features:
                expanded += [feature] * metadata[feature].get("colspan", 1)
            for ix, ftr in metadata["rowspan_features"].items():
                if ix not in expanded:
                    before = expanded[:ftr]
                    after = expanded[ftr:]
                    expanded = before + [ix] + after
            expanded_colspan_features[i] = expanded
        zipped_names = list(zip(*list(expanded_colspan_features.values())))
        zipped_names = [(t[0],'') if all_same(t) else t for t in zipped_names]
        # print(expanded_colspan_features)
        # print(zipped_names)
        feature_names = zipped_names
    return feature_names
```

``` python
def get_table_values(table):
    """Return the Feature values of a table element."""
    values = []
    sample_rows = table.find_all("tr")[1:]
    for sample_row in sample_rows:
        features = []
        for feature_col in sample_row.find_all("td"):
            n_spans = int(feature_col.attrs.get("colspan", 1))
            text = "".join(feature_col.find_all(string=True))
            lspaces = sum(1 for _ in itertools.takewhile(str.isspace, text))
            text = text[lspaces:]
            text = remove_wiki_refs(text).strip()
            text = remove_bracs_parens(text)
            if "," in text:
                x = text.replace(",", "").replace(" ", "")
                if x.isnumeric() or x.isdecimal() or x.isdigit():
                    [features.append(x) for _ in range(n_spans)]
                else:
                    [features.append(f"'{text}'") for _ in range(n_spans)]
            else:
                [features.append(text) for _ in range(n_spans)]
        values.append(features)
    return values

```

``` python
def get_table_data(table):
    """Get Table Data.

    Returns a list of dict objects key value pairs of
    [{feature_name[i] :feature_value[i],...},...].
    """
    samples = []
    feature_names = get_table_headers(table)
    sample_rows = get_table_values(table)
    for features in sample_rows:
        samples.append(dict(zip(feature_names, features)))
    return samples

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

def get_table_caption(table):
    """Return the caption of a table."""
    cap = table.find("caption")
    if cap is not None:
        return cap.text.strip()
    else:
        return ""



def print_table_values(table_values):
    """Print a formatted table feature_values or rows."""
    for row in table_values[:5]:
        print(",".join([i if i else "" for i in row]).replace("\n", ""))


def list_page_tables(tables):
    """Print all headers of all tables in tables."""
    for i, table in enumerate(tables):
        print(f"\n{'==='*13}> Table {i+1}")
        print("table caption: ", get_table_caption(table))
        print_table_headers(get_table_headers(table))
        print_table_values(get_table_values(table))
```

``` python
def to_pandas_dataframe(samples):
    """Convert table_data to pandas.DataFrame.

    Return the Extracted Table Data key,value samples to a Pandas DataFrame.
    """
    df = pd.DataFrame(samples).dropna(axis=0, how="all")
    columns = df.columns
    tup_cols = [c for c in columns if isinstance(c, tuple)]
    if len(tup_cols) == 0:
        return df
    ixs= [c for c in columns if not isinstance(c, tuple)]
    if len(ixs):
        ix=ixs[0]
        df = df.set_index(ix)
    df.columns = pd.MultiIndex.from_tuples(tup_cols)
    if len(ixs):
        ix=ixs[0]
        df = df.reset_index()
    return df
```

``` python
def obtain_table_data_by_number(N, tables):
    """Return the table data samples for the N^th table in wikipedia page."""
    return get_table_data(tables[N - 1])


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
    if not len(tables):
        print("0 Tables Found!\tExiting...")
    if args.save_all:
        if not args.outf:
            filename = get_filename_from_wikipedia_url(args.wikipedia_url)
        else:
            filename = args.outf
        for i in range(len(tables)):
            table = obtain_table_data_by_number(i + 1, tables)
            df = to_pandas_dataframe(table)
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
            table = obtain_table_data_by_number(i + 1, tables)
            df = to_pandas_dataframe(table)
            cols = df.columns
            if args.exclude_col:
                col = cols[args.exclude_col - 1]
                cols = [c for c in cols if c != col]
            save_to_json(df[cols], filename[:-4] + str(i) + ".json")
    if args.save_to_csv:
        N = int(args.N)
        table = obtain_table_data_by_number(N, tables)
        if not args.outf:
            filename = get_filename_from_wikipedia_url(args.wikipedia_url)
        else:
            filename = args.outf
        df = to_pandas_dataframe(table)
        cols = df.columns
        if args.exclude_col:
            col = cols[args.exclude_col - 1]
            cols = [c for c in cols if c != col]
        save_to_csv(df[cols], filename)
        return df[cols]
    else:
        filename = get_filename_from_wikipedia_url(args.wikipedia_url)
        list_page_tables(tables)
        print("\n")
        print(f"Default Output Filename: {filename}")
        dfs=[]
        for i in range(len(tables)):
            table = obtain_table_data_by_number(i + 1, tables)
            df = to_pandas_dataframe(table)
            cols = df.columns
            if args.exclude_col:
                col = cols[args.exclude_col - 1]
                cols = [c for c in cols if c != col]
            dfs.append(df[cols])
        return dfs
        

```

## Testing

``` python
# echo:true
dfs = run_table_extraction(
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
| 1   | World             | 109,529,216.00 | 2024 | 105,435,536.00 | 2023 | 100,834,800.00 | 2022 |
| 2   | United States     | 28,781,084.00  | 2024 | 27,360,936.00  | 2023 | 25,744,100.00  | 2022 |
| 3   | China             | 18,532,632.00  | 2024 | 17,794,782.00  | 2023 | 17,963,170.00  | 2022 |
| 4   | Germany           | 4,591,100.00   | 2024 | 4,456,081.00   | 2023 | 4,076,923.00   | 2022 |
| 5   | Japan             | 4,110,452.00   | 2024 | 4,212,945.00   | 2023 | 4,232,173.00   | 2022 |
| 6   | India             | 3,937,011.00   | 2024 | 3,549,919.00   | 2023 | 3,465,541.00   | 2022 |
| 7   | United Kingdom    | 3,495,261.00   | 2024 | 3,340,032.00   | 2023 | 3,089,072.00   | 2022 |
| 8   | France            | 3,130,014.00   | 2024 | 3,030,904.00   | 2023 | 2,775,316.00   | 2022 |
| 9   | Brazil            | 2,331,391.00   | 2024 | 2,173,666.00   | 2023 | 1,920,095.00   | 2022 |
| 10  | Italy             | 2,328,028.00   | 2024 | 2,254,851.00   | 2023 | 2,046,952.00   | 2022 |

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
| 201 | Samoa                 | 1,024.00 | 2024 | 934.00     | 2023 | 857.00         | 2022 |
| 202 | São Tomé and Príncipe | 751.00   | 2024 | 603.00     | 2023 | 546.00         | 2022 |
| 203 | Dominica              | 708.00   | 2024 | 654.00     | 2023 | 612.00         | 2022 |
| 204 | Tonga                 | 581.00   | 2024 | 500.00     | 2022 | 488.00         | 2022 |
| 205 | Micronesia            | 484.00   | 2024 | 460.00     | 2023 | 427.00         | 2022 |
| 206 | Kiribati              | 311.00   | 2024 | 279.00     | 2023 | 223.00         | 2022 |
| 207 | Palau                 | 308.00   | 2024 | 263.00     | 2023 | 225.00         | 2022 |
| 208 | Marshall Islands      | 305.00   | 2024 | 284.00     | 2023 | 279.00         | 2022 |
| 209 | Nauru                 | 161.00   | 2024 | 154.00     | 2023 | 147.00         | 2022 |
| 210 | Tuvalu                | 66.00    | 2024 | 62.00      | 2023 | 59.00          | 2022 |

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
| 71  | Kenya             | 104,001.00 | 2024 | 107,441.00 | 2023 | 113,419.00     | 2022 |

</div>

**Nominal GDP Per Capita in USD**

``` python
dfs2=run_table_extraction(
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
| 1   | Monaco            | NaN        | —    | 240,862.00 | 2022 | 234,317.00     | 2021 |
| 2   | Liechtenstein     | NaN        | —    | 187,267.00 | 2022 | 169,260.00     | 2021 |
| 3   | Luxembourg        | 131,384.00 | 2024 | 128,259.00 | 2023 | 133,745.00     | 2021 |
| 4   | Bermuda           | NaN        | —    | 123,091.00 | 2022 | 112,653.00     | 2021 |
| 5   | Ireland           | 106,059.00 | 2024 | 103,685.00 | 2023 | 101,109.00     | 2021 |
| 6   | Switzerland       | 105,669.00 | 2024 | 99,995.00  | 2023 | 93,525.00      | 2021 |
| 7   | Cayman Islands    | NaN        | —    | 96,074.00  | 2022 | 85,250.00      | 2021 |
| 8   | Norway            | 94,660.00  | 2024 | 87,962.00  | 2023 | 89,242.00      | 2021 |
| 9   | Isle of Man       | NaN        | —    | 94,124.00  | 2021 | NaN            | —    |
| 10  | Singapore         | 88,447.00  | 2024 | 84,734.00  | 2023 | 66,822.00      | 2021 |

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
| 214 | Sudan                    | 547.00   | 2024 | 2,272.00   | 2023 | 786.00         | 2021 |
| 215 | Madagascar               | 538.00   | 2024 | 529.00     | 2023 | 500.00         | 2021 |
| 216 | Central African Republic | 538.00   | 2024 | 445.00     | 2023 | 461.00         | 2021 |
| 217 | Sierra Leone             | 527.00   | 2024 | 433.00     | 2023 | 505.00         | 2021 |
| 218 | Yemen                    | 486.00   | 2024 | 533.00     | 2023 | 302.00         | 2021 |
| 219 | Malawi                   | 481.00   | 2024 | 673.00     | 2023 | 613.00         | 2021 |
| 220 | South Sudan              | 422.00   | 2024 | 1,072.00   | 2015 | 400.00         | 2021 |
| 221 | Afghanistan              | 422.00   | 2022 | 353.00     | 2022 | 373.00         | 2021 |
| 222 | Syria                    | NaN      | —    | 421.00     | 2021 | 925.00         | 2021 |
| 223 | Burundi                  | 230.00   | 2024 | 200.00     | 2023 | 311.00         | 2021 |

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
| 179 | Kenya             | 1,983.00 | 2024 | 1,950.00   | 2023 | 2,082.00       | 2021 |

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
| 11  | United States     | 85,373.00 | 2024 | 81,695.00  | 2023 | 69,185.00      | 2021 |

</div>
