### Pyblish Starter

A basic asset creation pipeline - batteries included.

<br>

- **Keywords:** Film, games, content creation, pipeline

- **Objective:**
    1. Provide an example of how one might go about building a pipeline around Pyblish.
    1. Demonstrate where publishing fits within a typical production pipeline
    1. Inspire further expansion upon basic ideas

- **Mission:** Demonstrate what is made possible with publishing.

- **Motivation:** I'm doing this for the same reason I created Pyblish. Because I see publishing as *the single most important aspect of any production pipeline*. It is on top of the advantages that it provides that the surrounding pipeline is made possible - e.g. [browser](#looking-ahead) and [loader](#looking-ahead), [builder](#looking-ahead) and [manager](#looking-ahead).

- **Requirements:** Reliably output correct data with minimal impact on artist productivity.

- **Technology:** Starter is built upon [Pyblish](http://pyblish.com), [Python](https://www.python.org) and [bindings](https://github.com/mottosso/Qt.py) for [Qt](https://qt.io), and depends upon a Windows, Linux or MacOS operating system with [Autodesk Maya](http://www.autodesk.com/maya).

- **Audience:** Technical directors interested in pipeline working in small- to mid-sized companies with a thirst for better ways of working.

- **Discaimer:** In the interest of simplicity, Starter is a very limited pipeline. If you have experience with an existing pipeline, or have thought about making your own, odds are this will look nothing like it. Take what you can from this project, and feel free to contribute your own ideas to make it simpler, or fork and expand upon it.

<br>

### Prerequisities

Before you start looking into pyblish-starter, it is recommended that you first familiarise yourself with Pyblish.

- [learn.pyblish.com](http://learn.pyblish.com)

<br>

### Target Audience

To make the most out of pyblish-starter, some knowledge and experience is assumed.

|                      | minimal                            | recommended             
|:---------------------|:-----------------------------------|:--------------
| **`personality`**    | curious                            | excited
| **`title`**          | technical director                 | pipeline technical director
| **`experience`**     | 1 year in advertisements or games  | 5+ years in feature film
| **`software`**       | windows, linux or macos            | maya

<br>
<br>

# Pyblish Starter

Welcome to pyblish-starter, a basic asset creation pipeline - batteries included.

<br>

**Table of contents**

- [Install](#install)
- [Usage](#usage)
- [Description](#description)
- [Batteries](#batteries)
    - [Creator](#creator)
    - [Loader](#loader)
- [Looking Ahead](#looking-ahead)
- [API](#api)
    - [Terminology](#terminology)
    - [Filesystem API](#filesystem-api)
        - [Information Hierarchy](#information-hierarchy)
        - [Workspace, Stage and Share](#workspace-stage-and-share)
        - [`ls()`](#ls)
        - [`asset.json`](#assetjson)
        - [`version.json`](#versionjson)
        - [`representation.json`](#representationjson)
    - [Starter API](#starter-api)
    - [Host API](#host-api)
- [Contract](#contract)
    - [`starter.model`](#startermodel)
    - [`starter.rig`](#starterrig)
    - [`starter.animation`](#starteranimation)
- [Homework](#homework)
- [Contributing](#contributing)
- Help

<br>
<br>

### Install

Starter takes the form of a Python package with embedded plug-ins.

```bash
$ pip install pyblish-starter
```

<br>
<br>

### Usage

Starter is initialised by calling `install()` with an interface for your host.

```python
>>> from pyblish_starter import install, maya
>>> install(maya)
```

From here, you model, rig and animate as per the [contract](#contract) below.

<br>
<br>

### Description

Build your own ASSET CREATION PIPELINE, starting with the basics.

**Overview**

*Asset creation* covers aspects related to producing content used in the production of film. A film is typically partitioned into sequences and shots, where each shot consists of one or more assets.

This project includes plug-ins and tools for 3 common types of ASSETS in a typical production pipeline.

- Modeling
- Rigging
- Animation

These illustrate how to **(1)** devise a contract - known as a `family` - for each *kind* of ASSET and **(2)** design their interface towards each other.

**Batteries included**

In addition to contracts, the project illustrates **boundaries** between publishing and setup. The definition of "setup" being anything that isn't strictly output, such as creating geometry or assigning attributes.

It includes a series of graphical user interfaces to aid the user in conforming to these contracts. These interfaces represent **placeholders** for your pipeline to fill in; you are invited to either continue from where they finish, or build your own from scratch.

<br>
<br>

### Batteries

In addition to providing a co-operative set of plug-ins, Starter also implements a minimal toochain for ASSET creation in a typical film pipeline.

<br>

<img align="right" src="https://cloud.githubusercontent.com/assets/2152766/18829363/d336cb5e-83d3-11e6-9634-efb2fa0914c5.png">

#### Creator

Associate content with a family.

The family is what determins how the content is handled throughout your pipeline and tells Pyblish what it should look like when valid.

**API**

The creator respects families registered with Starter.

```python
from pyblish_starter import api

api.register_family(
    name="my.family",
    help="My custom family"
)
```

For each family, a **common set of data** is automatically associated with the resulting instance.

```python
{
    "id": "pyblish.starter.instance",
    "family": {chosen family}
    "name": {chosen name}
}
```

**Additional common** data can be added.

```python
from pyblish_starter import api

api.register_data(
    key="myKey",
    value="My value",
    help="A special key"
```

Finally, data may be **associated** with a family.

```python
from pyblish_starter import api

api.register_family(
    name="my.family",
    data=[
        {"key": "name", "value": "marcus", "help": "Your name"},
        {"key": "age", "value": 30, "help": "Your age"},
])
```


<br>
<br>

<img align="right" src="https://cloud.githubusercontent.com/assets/2152766/18829392/f67c21a4-83d3-11e6-9047-6df5836317aa.png">

#### Loader

Visualise results from `api.ls()`.

```python
from pyblish_starter import api

for asset in api.ls():
    print(ASSET["name"])
```

**API**

The results from `api.ls()` depends on the currently **registered root**.

```python
from pyblish_starter import api

api.register_root("/projects/gravity")
```

The chosen `ASSET` is passed to the `load()` function of the currently registered host.

```python
from pyblish_starter import api, maya
api.register_host(maya)
```

A host is automatically registered on `pyblish_starter.install()`.

<br>
<br>
<br>
<br>
<br>
<br>
<br>

<br>
<br>

### Looking Ahead

Without publishing, in any shape or form, the following essential tools are but a dream.

| Name              | Purpose                          | Description
|:------------------|:---------------------------------|:--------------
| browser           | remove file-system dependence    | Search and clear presentation of available data relative a given project or task.
| loader            | control what goes in             | Keep tabs on where data comes from so as to enable tracking and builds.
| builder           | associate disparate ASSETS       | Automatic composition of data that changes independently but need to somehow stay associated.
| manager           | stay up to date                  | Notification and visualisation of data in time.

<br>

**Ideas**

Here are a few things you might want to implement now that you have a solid framework upon which to build.

- Add a **thumbnail** to ASSETS by automatically extracting one per instance
- Enable **search** in Loader, and augment it by extracting additional metadata about an ASSET, such as `author`, `use`, `size`, `origin` or `datatype`.

<br>
<br>

# API

Starter exposes a series of interrelated APIs to the end-user.

| Name                          | Purpose
|:------------------------------|:--------------
| [Filesystem API](#filesystem-api) | Defines how the **developer** interact with **data** on disk
| [Starter API](#starter-api)       | Defines how the **developer** interacts with **Starter**
| [Host API](#host-api)             | Defines how the **host** interacts with **Starter**

<br>
<br>

### Terminology

Starter reserves the following words for private and public use. Public members are exposed to the user, private ones are internal to the implementation.

|          | Term                | Public | Description         | Example
|:---------|:--------------------|:-------|:--------------------|:------------------------
| ![][pro] | `PROJECT`           | `X`    | Root of information | Gravity, Dr. Strange
| ![][ast] | `ASSET`             | `X`    | Unit of data        | Ryan, Bicycle, Flower pot
| ![][ver] | `VERSION`           | `X`    | An ASSET iteration  | v1, v034
| ![][rep] | `REPRESENTATION`    |        | A data format       | Maya file, pointcache, thumbnail
| ![][for] | `FORMAT`            |        | A file extension    | `.ma`, `.abc`, `.ico`, `.png`
| ![][usr] | `WORKSPACE`         | `X`    | Private data        | Scenefile for v034 of Ryan
| ![][stg] | `STAGE`             |        | Transient data      | Outgoing VERSION from scenefile
| ![][shd] | `SHARED`            | `X`    | Public data         | v034 of Ryan
| ![][prd] | `PRODUCER`          |        | Creator of data     | You
| ![][cns] | `CONSUMER`          |        | User of data        | Me

<br>
<br>

### Filesystem API

Data is organised into **files** and **folders**.

Some files and folders have special meaning in Starter.

![image](https://cloud.githubusercontent.com/assets/2152766/18836965/03e2f018-83fa-11e6-81d5-2dcfa19c43ab.png)

<br>

### Information Hierarchy

The mental and physical model for files and folders look like this.

![temp_03](https://cloud.githubusercontent.com/assets/2152766/18833936/1aba9bba-83eb-11e6-812c-2104f7bb3e2a.png)

<br>
<br>

### Workspace, Stage and Share

During the course of the creation of any ASSET, data moves between 2 of 3 states.

![temp](https://cloud.githubusercontent.com/assets/2152766/18838199/798a132e-83fe-11e6-8c1f-f515978d6ce2.png)

- Starter does not take into consideration the workspace and is therefore **workspace-agnostic**. 
- The **staging area** is both implicit and transparent to the PRODUCER and CONSUMER, except for debugging purposes. This is where automatic/scheduled garbage collection may run to optimise for space constraints.
- The **shared space** is where ASSETS ultimately reside once published.

<br>

**Workspace and Shared separation**

A naive approach to content creation might be to refer to ASSETS straight from another artists workspace. Starter separates between data considered work-in-progress and data exposed to others.

Workspace data is highly **mutable** and typically **private** to an individual artist.

- **Mutable** implies transient data that is likely to change at any given moment.
- **Private** implies personal, highly irregular and likely invalid data.

Shared data on the other hand is **immutable**, **correct** and **impersonal**.

- **Immutable** implies that the data may be dependent upon by other data.
- **Correct** implies passing validation of the associated family.
- **Impersonal** implies following strict organisational conventions.

[ver]: https://cloud.githubusercontent.com/assets/2152766/18576835/f6b80574-7bdc-11e6-8237-1227f779815a.png
[ast]: https://cloud.githubusercontent.com/assets/2152766/18576836/f6ca19e4-7bdc-11e6-9ef8-3614474c58bb.png
[rep]: https://cloud.githubusercontent.com/assets/2152766/18759916/b2e3161c-80f6-11e6-9e0a-c959d63047a8.png
[for]: https://cloud.githubusercontent.com/assets/2152766/18759918/b479168e-80f6-11e6-8d1c-aee4e654d335.png
[pro]: https://cloud.githubusercontent.com/assets/2152766/18760901/d6bf24b4-80fa-11e6-8880-7a0e927c8c27.png
[usr]: https://cloud.githubusercontent.com/assets/2152766/18808940/eee150bc-8267-11e6-862f-a31e38d417af.png
[shd]: https://cloud.githubusercontent.com/assets/2152766/18808939/eeded22e-8267-11e6-9fcb-150208d55764.png
[stg]: https://cloud.githubusercontent.com/assets/2152766/18835951/9dbaf5d2-83f5-11e6-9ea4-fbbb5f1d0e13.png
[prd]: https://cloud.githubusercontent.com/assets/2152766/18836255/163d70a6-83f7-11e6-94b7-2f65a2c3b53b.png
[cns]: https://cloud.githubusercontent.com/assets/2152766/18836254/163d1124-83f7-11e6-9575-05a523a364fb.png

<br>
<br>

Each **ASSET** reside within the top-level **root** directory as follows.

| Hierarchy       | Example
|:----------------|:--------------
| ![hier][]       | ![hierex][]

<br>

Each ASSET contain 0 or more **versions** which in turn contain 0 or more **representations**.

| Hierarchy       | Example
|:----------------|:--------------
| ![org][]        | ![exm][]

<br>

Every extraction is made into the **staging** directory, regardless of whether it integrates successfully or not.

| Hierarchy     | Example
|:--------------|:------------
| ![usr1][]     | ![usr2][]

Each directory will contain everything that did extract successfully, along with its metadata, for manual inspection and debugging.

[hier]: https://cloud.githubusercontent.com/assets/2152766/18818198/3388a630-836b-11e6-9202-8728496d8561.png
[hierex]: https://cloud.githubusercontent.com/assets/2152766/18818207/64ef8112-836b-11e6-83f7-0ec187c605ff.png

[org]: https://cloud.githubusercontent.com/assets/2152766/18817999/a6a35742-8365-11e6-851f-6e5911b4c885.png
[exm]: https://cloud.githubusercontent.com/assets/2152766/18818169/411fe7c8-836a-11e6-9a8c-14c39e6a072d.png

[usr1]: https://cloud.githubusercontent.com/assets/2152766/18834482/07938972-83ee-11e6-92d0-1a989c2b54dd.png
[usr2]: https://cloud.githubusercontent.com/assets/2152766/18834427/ab4b319c-83ed-11e6-8e72-2bf59e83b8d5.png

<br>

### `ls()`

Communication with the filesystem is made through `ls()`.

`ls()` returns available assets - relative the currently registered root directory - in the form of JSON-compatible dictionaries. Each dictionary is strictly formatted according to three distinct ["schemas"](https://en.wikipedia.org/wiki/Database_schema) (see below).

See below for a full list of members.

**Example**

```python
import pyblish_starter

for asset in pyblish_starter.ls():
    assert "versions" in asset

    for version in asset["versions"]:
        assert "representations" in version

        for representation in version["representations"]:
            pass
```

<br>

**Schemas**

![temp_08](https://cloud.githubusercontent.com/assets/2152766/18837249/f7568e26-83fa-11e6-9bdf-e2d369bf2394.png)

Available schemas are organised hierarchically, with the former containing the latter.

- [`asset.json`](#assetjson)
  - [`version.json`](#versionjson)
    - [`representation.json`](#representationjson)

<br>

#### [`asset.json`][]

A unit of data

| Key               | Value  | Description
|:------------------|:-------|:-------------
| `name`            | `str`  | Name of directory
| `versions`        | `list` | 0 or more [`version.json`](#versionjson)

[`asset.json`]: https://github.com/pyblish/pyblish-starter/blob/master/pyblish_starter/schema/asset.json

<br>

#### [`version.json`][]

An ASSET iteration

| Key               | Value  | Description
|:------------------|:-------|:-------------
| `version`         | `int`  | Number of this VERSION
| `path`            | `str`  | Unformatted path
| `time`            | `str`  | ISO formatted, file-system compatible time.
| `author`          | `str`  | User logged on to the machine at time of publish.
| `source`          | `str`  | Original file from which this VERSION was made.
| `representations` | `list` | 0 or more [`representation.json`](#representationjson)

[`version.json`]: https://github.com/pyblish/pyblish-starter/blob/master/pyblish_starter/schema/version.json

<br>

#### [`representation.json`][]

A data FORMAT.

| Key               | Value  | Description
|:------------------|:-------|:-------------
| `format`          | `str`  | File extension
| `path`            | `str`  | Unformatted path

[`representation.json`]: https://github.com/pyblish/pyblish-starter/blob/master/pyblish_starter/schema/representation.json

<br>
<br>

### Starter API

pyblish-starter provides a stateful API.

State is set and modified by calling any of the exposed registration functions, prefixed `register_*`, or automatically on calling `pyblish_starter.install()`.

<br>

Public members of `pyblish_starter`

| Member                           | Returns  | Description
|:---------------------------------|:---------|:--------
| `install(host)`                  | `str`    | Install Starter into the current interpreter session
| `uninstall()`                    | `str`    | Revert installation

<br>

Public members of `pyblish_starter.api`

| Member                           | Returns  | Description
|:---------------------------------|:---------|:--------
| `ls()`                           | `generator` | List available assets, relative `root`
| `root()`                         | `str`       | Absolute path to current working directory
| `format_staging_dir(root, name)` | `str`       | Return absolute path or staging directory relative arguments
| `format_shared_dir(root)`        | `str`       | Return absolute path of shared directory
| `format_version(version)`        | `str`       | Return file-system compatible string of `version`
| `find_latest_version(versions)`  | `int`       | Given a series of string-formatted versions, return the latest one
| `parse_version(version)`         | `str`       | Given an arbitrarily formatted string, return version number
| `register_root(root)`            |             | Register currently active root
| `register_host(host)`            |             | Register currently active host
| `register_plugins()`             |             | Register plug-ins bundled with Pyblish Starter
| `deregister_plugins()`           |             |
| `registered_host()`              | `module`    | Return currently registered host
| `registered_families()`          | `list`      | Return currently registered families
| `registered_data()`              | `list`      | Return currently registered data
| `registered_root()`              | `str`       | Return currently registered root

<br>
<br>

### Host API

A host must implement the following members.

| Member                    | Returns    | Description
|:--------------------------|:-----------|:--------
| `ls()`                    | `generator`| List loaded assets
| `create(name, family)`    | `dict`     | Build fixture for outgoing data (see [instance]())
| `load(asset, version=-1)` | `str`      | Import external data into [container]()

<br>

Some data within a host is special, and is identified via custom "tags".

| Name                         | Description              | Example
|:-----------------------------|:-------------------------|:----------
| `pyblish.starter.container`  | Unit of incoming data    | `...:model_GRP`, `...:rig_GRP` 
| `pyblish.starter.instance`   | Unit of outgoing data    | `Strange_model_default`

<br>
<br>

### Contract

![image](https://cloud.githubusercontent.com/assets/2152766/18839192/ff4f9670-8401-11e6-8b8b-750d96d83bbd.png)

Starter defines these families.

| Family              | Definition                                     | Link
|:--------------------|:-----------------------------------------------|:------------
| `starter.model`     | Geometry with deformable topology              | [Spec](#startermodel)
| `starter.rig`       | An articulated `starter.model` for animators   | [Spec](#starterrig)
| `starter.animation` | Pointcached `starter.rig` for rendering        | [Spec](#starteranimation)

<br>

### `starter.model`

<img align="right" src="https://cloud.githubusercontent.com/assets/2152766/18526694/7453567a-7ab9-11e6-817c-84a874092399.png"/>

A generic representation of geometry.

![aud][] **Target Audience**

- Texturing
- Rigging
- Final render

![req][] **Requirements**

- All DAG nodes must be parented to a single top-level transform
- Normals must be unlocked

![dat][] **Data**

- `name (str, optional)`: Pretty printed name in graphical user interfaces

![set][] **Sets**

- `geometry_SEL (geometry)`: Meshes suitable for rigging
- `aux_SEL (any, optional)`: Auxilliary meshes for e.g. fast preview, collision geometry

<br>
<br>
<br>
<br>

### `starter.rig`

<img align="right" src="https://cloud.githubusercontent.com/assets/2152766/18526730/9c7f040a-7ab9-11e6-9007-4795ddbadde8.png"/>

The `starter.rig` contains the necessary implementation and interface for animators to animate. 

![aud][] **Target Audience**

- Animation

![req][] **Requirements**

- All DAG nodes must be parented to a single top-level transform
- Must contain an `objectSet` for controls and cachable geometry

![dat][] **Data**

- `name (str, optional)`: Pretty printed name in graphical user interfaces

![set][] **Sets**

- `cache_SEL (geometry)`: Meshes suitable for pointcaching from animation
- `controls_SEL (transforms)`: All animatable controls
- `resources_SEL (any, optional)`: Nodes that reference an external file

<br>
<br>

### `starter.animation`

<img align="right" src="https://cloud.githubusercontent.com/assets/2152766/18526738/a0fba5ba-7ab9-11e6-934f-48ca2a2ce3d2.png"/>

Point positions and normals represented as one Alembic file.

![aud][] **Target Audience**

- Lighting
- FX
- Cloth
- Hair

![req][] **Requirements**

- None

![dat][] **Data**

- `name (str, optional)`: Pretty printed name in graphical user interfaces

![set][] **Sets**

- None

<br>

**Legend**

|          | Title               | Description
|:---------|:--------------------|:-----------
| ![aud][] | **Target Audience** | Who is the end result of this family intended for?
| ![req][] | **Requirements**    | What is expected of this ASSET before it passes the tests?
| ![dat][] | **Data**            | End-user configurable options
| ![set][] | **Sets**            | Collection of specific items for publishing or use further down the pipeline.


[set]: https://cloud.githubusercontent.com/assets/2152766/18576835/f6b80574-7bdc-11e6-8237-1227f779815a.png
[dat]: https://cloud.githubusercontent.com/assets/2152766/18576836/f6ca19e4-7bdc-11e6-9ef8-3614474c58bb.png
[req]: https://cloud.githubusercontent.com/assets/2152766/18576838/f6da783e-7bdc-11e6-9935-78e1a6438e44.png
[aud]: https://cloud.githubusercontent.com/assets/2152766/18576837/f6d9c970-7bdc-11e6-8899-6eb8686b4173.png

<br>
<br>

# Homework

With an understanding of this asset creation pipeline, here are some suggestions for what to explore next.

| Difficulty       | Task                | Description
|------------------|:--------------------|:-----------------
| ![easy][]        | Loader tooltip      | Pick any of the available data from an asset, and add it to the tooltip of the item.
| ![hard][]        | Shots               | Think of and document how the kind of workflow exemplified here - (1) creating, (2) publishing and (3) loading assets - can be applied to a shot- and task-based pipeline.
| ![challenging][] | A Creator Help Page | The creator interface is very limited. Try including a help-page and picture alongside each family illustrating what each are for.
| ![hard][]        | Loader thumbnails   | The loader interface is even more limited, with room for expansion. Consider how you might go about extracting a thumbnail alongside each asset, and add it to the interface.

[easy]: https://cloud.githubusercontent.com/assets/2152766/18850396/3cdcdfc0-842f-11e6-916d-1936dde45d94.png
[challenging]: https://cloud.githubusercontent.com/assets/2152766/18850397/3cf15b44-842f-11e6-8f75-a38933d11e0b.png
[hard]: https://cloud.githubusercontent.com/assets/2152766/18850398/3cf84314-842f-11e6-9d93-58d3e96f6f7d.png

<br>
<br>

# Contributing

pyblish-starter, as Pyblish itself, is an open source effort and contributions are welcome.

For example, you could fork Starter, expand upon the graphical user interfaces and either make it your own or submit a pull-request to have it merge with the official project.

For more information on this, contact [me](mailto:marcus@abstractfactory.io) and let's have a conversation!
