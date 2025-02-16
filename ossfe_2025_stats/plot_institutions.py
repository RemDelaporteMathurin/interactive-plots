import pycountry_convert as pc
import pandas as pd
import plotly.express as px
from pypalettes import load_cmap
import matplotlib.colors as mcolors


cmap = load_cmap("blaziken")

# read registrations.csv

df = pd.read_csv("registrations.csv")

# remove all line breaks
df = df.replace("\n", " ", regex=True)

df = df[["First name", "Last name", "Country", "Institution"]]

# remove trailing whitespaces from country names
df["Country"] = df["Country"].str.strip()
# replace double spaces by single space
df["Country"] = df["Country"].str.replace("  ", " ")


def lookup_country(name: str, *, allow_fuzzy: bool = False) -> str | None:
    """Lookup country name by country `name` using `pycountry`."""

    import pycountry

    # Handle special cases
    if name == "UK":
        name = "United Kingdom"
    elif name == "Russia":
        name = "Russian Federation"
    elif name == "The Netherlands":
        name = "Netherlands"

    if country := pycountry.countries.get(name=name):
        return country.name

    try:
        return pycountry.countries.lookup(name).name
    except LookupError:
        pass

    try:
        return (
            pycountry.countries.search_fuzzy(query=name)[0].name
            if allow_fuzzy
            else None
        )
    except (LookupError, IndexError):
        return None


# Apply the function to standardize country names
for country_name in df["Country"].unique():
    assert (
        lookup_country(country_name) is not None
    ), f"Country name {country_name} not found"

df["Country"] = df["Country"].apply(lookup_country)

# show where the country name is None
assert df["Country"].isnull().sum() == 0, "Some country names are None"


# Function to get continent name from country name
def get_continent(country_name):
    try:
        country_alpha2 = pc.country_name_to_country_alpha2(country_name)
        continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
        continent_name = pc.convert_continent_code_to_continent_name(continent_code)
        return continent_name
    except:
        return "Unknown"


# Add continent column
df["Continent"] = df["Country"].apply(get_continent)

institution_map = {
    "UKAEA": "UKAEA",
    "UK Atomic Energy Authority": "UKAEA",
    "Imperial College London/UK Atomic Energy Authority": "Imperial College London",
    "York Plasma Institute, University of York": "University of York",
    "HI IBERIA (HIB) https://www.hi-iberia.es/artificial-intelligence": "HI IBERIA",
    "HI-Iberia": "HI IBERIA",
    "HI Iberia": "HI IBERIA",
    "HI-Iberia, University Carlos II, Gregorio Millán Barbany Institute": "HI IBERIA",
    "ATG Engineering S.L": "ATG Engineering S.L.",
    "VTT Research Center of Finland": "VTT Technical Research Centre of Finland Ltd",
    "CEA/IRFM": "CEA",
    "CEA IRFM": "CEA",
    "MIT": "Massachusetts Institute of Technology",
    "General Fusion": "General Fusion Inc.",
    "MIT PSFC": "Massachusetts Institute of Technology",
    "ntTau Digital": "nTtau Digital LTD",
    "Proxima Fusion GmbH": "Proxima Fusion",
    "University of York Plasma Institute": "University of York",
}

# remove all trailing whitespaces from institutions
df["Institution"] = df["Institution"].str.strip()


def standardise_institutions(institution):
    return institution_map.get(institution, institution)


df["Institution"] = df["Institution"].apply(standardise_institutions)

# # compute number of registrations per country
df = (
    df.groupby(["Continent", "Country", "Institution"]).size().reset_index(name="count")
)
# Map colors to unique continents
unique_continents = (
    df.groupby("Continent")["count"].sum().sort_values(ascending=False).index
)

color_map = {
    continent: mcolors.to_hex(cmap(i / (len(unique_continents) - 1)))
    for i, continent in enumerate(unique_continents)
}
df["color"] = df["Continent"].map(color_map)


# make a treemap grouped by continent
fig = px.treemap(
    df,
    path=["Continent", "Country", "Institution"],  # Specify the hierarchy
    values="count",  # Specify the values
    color="Continent",  # Color by continent
    color_discrete_map=color_map,  # Set the color map
    custom_data=df[["count"]],  # Add custom data for the count
    hover_data={"count": ":.0f"},  # Format the count
    labels={"count": "Registrations"},
)


fig.update_traces(texttemplate="%{label} %{customdata[0]}")  # Show label and count
# export to html
fig.write_html("output.html")
fig.show()
