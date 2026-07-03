# Report QGIS 4.2

Riepilogo generato dal changelog QGIS 4.2.

## Panoramica

- **Feature totali:** 59
- **Categorie:** 17
- **Sviluppatori distinti:** 24
- **Finanziatori distinti:** 8
- **Feature con sviluppatore indicato:** 59/59 (100%)
- **Feature con finanziatore indicato:** 21/59 (36%)

## Feature per categoria

| Categoria | Feature | |
|---|--:|:--|
| 3D Features | 12 | `████████████████████████` |
| Symbology | 10 | `████████████████████····` |
| Notable Fixes | 8 | `████████████████········` |
| Point Clouds | 6 | `████████████············` |
| Processing | 5 | `██████████··············` |
| Print Layouts | 3 | `██████··················` |
| Data Providers | 3 | `██████··················` |
| Expressions | 2 | `████····················` |
| QGIS Server | 2 | `████····················` |
| Breaking Changes | 1 | `██······················` |
| User Interface | 1 | `██······················` |
| Data Management | 1 | `██······················` |
| Application and Project Options | 1 | `██······················` |
| Sensors | 1 | `██······················` |
| Profile Plots | 1 | `██······················` |
| Browser | 1 | `██······················` |
| Programmability | 1 | `██······················` |

## Top sviluppatori

| # | Sviluppatore | Feature | Azienda |
|--:|---|--:|---|
| 1 | Nyall Dawson | 19 | North Road |
| 2 | Dominik Cindric | 9 | — |
| 3 | Jean Felder | 3 | Oslandia |
| 4 | Julien Cabieces | 3 | Oslandia |
| 5 | Martin Dobias | 3 | Lutra Consulting |
| 6 | Stefanos Natsis | 3 | Lutra Consulting |
| 7 | Mathieu Pellerin | 2 | OPENGIS.ch |
| 8 | Jan Caha | 1 | — |
| 9 | David Koňařík | 1 | — |
| 10 | Germap | 1 | — |
| 11 | Patrice Pineault | 1 | — |
| 12 | Jacky Volpes | 1 | Oslandia |
| 13 | Alexander Bruy | 1 | QCooperative |
| 14 | Norman Barker | 1 | — |
| 15 | Sandro Mani | 1 | — |

## Feature per azienda (via mappatura sviluppatori)

| Azienda | Feature |
|---|--:|
| North Road | 19 |
| Oslandia | 7 |
| Lutra Consulting | 6 |
| OPENGIS.ch | 2 |
| QCooperative | 2 |

## Finanziatori

| Finanziatore | Feature |
|---|--:|
| QGIS.ORG (through donations and sustaining memberships) | 8 |
| Stadt Frankfurt am Main | 3 |
| Stadt Frankfurt am Main and Oslandia | 3 |
| République et canton de Genève | 3 |
| Natural Resources Canada | 1 |
| the city of Bern | 1 |
| City of Canning | 1 |
| QGIS user group Germany (QGIS Anwendergruppe Deutschland e.V.) | 1 |

## Elenco completo delle feature

### 3D Features

- **Generate environmental lighting from skybox** — dev: *Nyall Dawson*
- **Support 3D model instancing** — dev: *Dominik Cindric*
- **Allow control over 3d map color grading effects** — dev: *Nyall Dawson*
- **Optional light bloom effects** — dev: *Nyall Dawson*
- **Add multisample anti aliasing (MSAA)** — dev: *Dominik Cindric*
- **Add gradient background to 3D scene** — dev: *Dominik Cindric*
- **3D Tiles: add instancing support** — dev: *Martin Dobias* · fondi: *Natural Resources Canada*
- **Add implicit tiling for 3D Tiles** — dev: *Martin Dobias*
- **Add camera controls dialog to control the 3D camera in map coordinates** — dev: *Dominik Cindric*
- **Add support for 3D composite tiles ("cmpt")** — dev: *Martin Dobias*
- **Improve 3D map view "Invert vertical axis" setting.** — dev: *David Koňařík*
- **3d export stl** — dev: *Jean Felder* · fondi: *Stadt Frankfurt am Main*

### Symbology

- **Add categorized renderer for 3D Symbols** — dev: *Jean Felder* · fondi: *Stadt Frankfurt am Main*
- **Add physically based material with texture support** — dev: *Nyall Dawson*
- **Add trim distance start and end to Hashes/Markers line symbol layer** — dev: *Julien Cabieces* · fondi: *Stadt Frankfurt am Main and Oslandia*
- **Add data-defined control for metal rough base, emission color** — dev: *Nyall Dawson*
- **Data defined control over phong/metal rough texture scale, rotation and offset** — dev: *Nyall Dawson*
- **Add optional solid emission color to metal rough material** — dev: *Nyall Dawson*
- **Add opacity support to metal rough materials** — dev: *Nyall Dawson*
- **Add 3d material settings to style database** — dev: *Nyall Dawson*
- **Allow choice of up/forward axis for 3d point model symbols** — dev: *Nyall Dawson*
- **Add extra items for templated line symbol layer** — dev: *Julien Cabieces* · fondi: *Stadt Frankfurt am Main and Oslandia*

### Notable Fixes

- **Bug fixes by Even Rouault (Spatialys)** — dev: *Even Rouault (Spatialys)* · fondi: *QGIS.ORG (through donations and sustaining memberships)*
- **Bug fixes by Denis Rouzaud (OPENGIS.ch)** — dev: *Denis Rouzaud (OPENGIS.ch)* · fondi: *QGIS.ORG (through donations and sustaining memberships)*
- **Bug fixes by Alessandro Pasotti (QCooperative)** — dev: *Alessandro Pasotti (QCooperative)* · fondi: *QGIS.ORG (through donations and sustaining memberships)*
- **Bug fixes by Julien Cabieces (Oslandia)** — dev: *Julien Cabieces (Oslandia)* · fondi: *QGIS.ORG (through donations and sustaining memberships)*
- **Bug fixes by Germán Carrillo (OPENGIS.ch)** — dev: *Germán Carrillo (OPENGIS.ch)* · fondi: *QGIS.ORG (through donations and sustaining memberships)*
- **Bug fixes by David Signer (OPENGIS.ch)** — dev: *David Signer (OPENGIS.ch)* · fondi: *QGIS.ORG (through donations and sustaining memberships)*
- **Bug fixes by Stefanos Natsis (Lutra Consulting)** — dev: *Stefanos Natsis (Lutra Consulting)* · fondi: *QGIS.ORG (through donations and sustaining memberships)*
- **Bug fixes by Loïc Bartoletti (Oslandia)** — dev: *Loïc Bartoletti (Oslandia)* · fondi: *QGIS.ORG (through donations and sustaining memberships)*

### Point Clouds

- **Add overview-length optional parameter to build vpc algorithm** — dev: *Stefanos Natsis*
- **Add reading support for multi-overview VPC files** — dev: *Stefanos Natsis*
- **Add support for a vpc-in-zip (.vpz) virtual point cloud format** — dev: *Stefanos Natsis*
- **Add per layer elevation shading** — dev: *Dominik Cindric*
- **Support arithmetic operators on color objects in expressions** — dev: *Dominik Cindric*
- **Modify renderer color by expression** — dev: *Dominik Cindric*

### Processing

- **Dynamically show child step feature counts as model progresses** — dev: *Nyall Dawson* · fondi: *City of Canning*
- **Add an area threshold parameter** — dev: *Jacky Volpes*
- **Add support for the SFCGAL extend to edges parameter in medial axis algorithm** — dev: *Jean Felder* · fondi: *Stadt Frankfurt am Main*
- **Add processing in user defined menu or toolbar** — dev: *Julien Cabieces* · fondi: *Stadt Frankfurt am Main and Oslandia*
- **Random subset algorithms ported to C++** — dev: *Alexander Bruy*

### Print Layouts

- **Add new layout chart item functionality to derive plot data and styling from the source vector layer renderer** — dev: *Mathieu Pellerin*
- **Add new option to clip a picture item by a shape-based item** — dev: *Mathieu Pellerin*
- **Geospatial PDF layer management enhancement** — dev: *Germap* · fondi: *the city of Bern*

### Data Providers

- **Greatly speed up the FeatureServer provider for map viewing** — dev: *Nyall Dawson* · fondi: *République et canton de Genève*
- **Enable parallel provider load for AFS, AMS providers, and some related fixes** — dev: *Nyall Dawson* · fondi: *République et canton de Genève*
- **Support STAC assets from other cloud optimized data types and blob stores** — dev: *Norman Barker*

### Expressions

- **Add scale_cubic_bezier expression function, handle bezier-cubic interpolation when converting MapBox styles** — dev: *Nyall Dawson*
- **Add concat_ws expression function** — dev: *Nyall Dawson*

### QGIS Server

- **Add support for HIGHLIGHT_LABELFRAME options WMS params** — dev: *Sandro Mani*
- **FlatGeobuf OAPIF export plus various fixes** — dev: *Alessandro Pasotti* · fondi: *QGIS user group Germany (QGIS Anwendergruppe Deutschland e.V.)*

### Breaking Changes

- **Move QGIS4 settings storage location with automated migration from QGIS3** — dev: *Nyall Dawson*

### User Interface

- **Add layer menu to load and save styles** — dev: *Jan Caha*

### Data Management

- **Adding "Field Calculator" menu item to the attribute table header** — dev: *Patrice Pineault*

### Application and Project Options

- **Topocentric projection** — dev: *Dominik Cindric*

### Sensors

- **Add support for SensorThings 2.0, including Sensing, Sampling and Relations extensions** — dev: *Nyall Dawson*

### Profile Plots

- **Display elevation profile curve in 3D** — dev: *Dominik Cindric*

### Browser

- **Rework how ESRI REST services are exposed in the browser** — dev: *Nyall Dawson* · fondi: *République et canton de Genève*

### Programmability

- **Expose concave hull of polygons functionality** — dev: *Nyall Dawson*
