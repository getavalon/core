### Pyblish Starter

A basic asset creation pipeline - batteries included.

- **Keywords:** Film, games, content creation, pipeline

- **Objective:**
    1. Introduce publishing to the techincal director
    1. Demonstrate where publishing fits within a typical production pipeline
    1. Inspire further expansion upon basic ideas

- **Mission:** Demonstrate what is made possible with publishing.

- **Motivation:** I'm doing this for the same reason I created Pyblish. Because I see publishing as *the single most important aspect of any production pipeline*. It is on top of the advantages that it provides that the surrounding pipeline is made possible - e.g. [browser](#looking-ahead) and [loader](#looking-ahead), [builder](#looking-ahead) and [manager](#looking-ahead).

- **Requirements** Reliably output correct data with minimal impact on artist productivity.

- **Technology** Starter is built upon [Pyblish](http://pyblish.com), [Python](https://www.python.org) and [bindings](https://github.com/mottosso/Qt.py) for [Qt](https://qt.io), and depends upon a Windows, Linux or MacOS operating system with [Autodesk Maya](http://www.autodesk.com/maya).

- **Audience** Technical directors interested in pipeline working in small- to mid-sized companies with a thirst for better ways of working.

<br>

**Table of contents**

- [Install](#install)
- [Usage](#usage)
- [Description](#description)
- [Batteries](#batteries)
- [Looking Ahead](#looking-ahead)
- [Terminology](#terminology)
- [Shared/User Separation](#shareduser-separation)
- [Ids](#ids)
- [Starter API](#starter-api)
- [Host API](#host-api)
- [Information Hierarchy](#information-hierarchy)
- [Contract](#contract)
    - [`starter.model`](#startermodel)
    - [`starter.rig`](#starterrig)
    - [`starter.animation`](#starteranimation)
- [Example](#example)
- [Requirement Specification](#requirement-specification)
    - [Workout](#workout)
    - [Self-intersections](#self-intersections)
    - [Extreme Acceleration](#extreme-acceleration)
    - [Extreme Surface Tangency](#extreme-surface-tangency)
    - [Extreme Surface Stretch or Compression](#extreme-surface-stretch-or-compression)
- Contributing
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

Build your own asset creation pipeline, starting with the basics.

**At a glance**

- Categorise nodes within your workfile as being part of a single asset.
- Enable an asset library to identify published data on disk.
- Track when, where and from whom each asset come from.

**Overview**

Asset creation covers all aspects related to building the assets used in the production of film. A film is typically partitioned into sequences and shots, where each shot consists of one or more assets.

This project includes interface and implementation for 3 common types of assets a typical production pipeline.

- Modeling
- Rigging
- Animation

The project illustrates how to **(1)** devise a contract - known as a `family` - for each kind of asset and **(2)** design their interface towards each other. For example, it is important for rendering and effects that the normals of each geometric surface is unlocked.

**Batteries included**

In addition to contracts, the project illustrates **boundaries** between publishing and setup. The definition of "setup" being anything that isn't strictly output, such as creating geometry or assigning attributes.

It includes a series of graphical user interfaces to aid the user in conforming to these contracts. These interfaces represent **placeholders** for your pipeline to fill in; you are invited to either continue from where they finish, or build your own from scratch.

<br>
<br>

### Batteries

In addition to Pyblish cooperative plug-ins, a series of template workflow utilities are included.

<img align="right" src="https://cloud.githubusercontent.com/assets/2152766/18809620/b31ed30e-8278-11e6-8d76-13fdcab71e52.png">

#### Creator

A bla bla bla, and a bla bla.

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>

<img align="right" src="https://cloud.githubusercontent.com/assets/2152766/18809647/67043f62-8279-11e6-8eb9-29b124040d6d.png">

#### Loader

A bla bla bla, and a bla bla.

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
| builder           | associate disparate assets       | Automatic composition of data that changes independently but need to somehow stay associated.
| manager           | stay up to date                  | Notification and visualisation of data in time.

<br>
<br>

### Terminology

Starter reserves the following words for private and public use. Public members are exposed to the user, private ones are internal to the implementation.

|          | Term                | Public | Description         | Example
|:---------|:--------------------|:-------|:--------------------|:------------------------
| ![][pro] | `project`           | `X`    | Root of information | Gravity, Dr. Strange
| ![][ast] | `asset`             | `X`    | Unit of data        | Ryan, Bicycle, Flower pot
| ![][ver] | `version`           | `X`    | An asset iteration  | v1, v034
| ![][rep] | `representation`    |        | A data format       | Maya file, pointcache, thumbnail
| ![][for] | `format`            |        | A file extension    | `.ma`, `.abc`, `.ico`, `.png`
| ![][shd] | `shared`            | `X`    | Public data         | v034 of Ryan
| ![][usr] | `user`              | `X`    | Private data        | Scenefile for v034 of Ryan

<br>

### Shared/User separation

Humans are imperfect, yet strive for perfection. In order to reduce the amount of friction produced through this contradiction, a separation is made between **user** and **shared** data. Artists are not required to work any differently, yet are able to produce correct data.

User data is highly **mutable** and typically **private** to an individual artist.

- **Mutable** implies transient data that is likely to change at any given moment.
- **Private** implies personal, highly irregular and likely invalid data.

Shared data on the other hand is **immutable**, **correct** and **impersonal**.

- **Immutable** implies that the data may be dependent upon by other data.
- **Correct** implies passing validation of the associated family.
- **Impersonal** implies following strict organisational conventions.

### Ids

...

| Name                         | Description              | Example
|:-----------------------------|:-------------------------|:----------
| `pyblish.starter.container`  | Unit of incoming data    | `...:model_GRP`, `...:rig_GRP` 
| `pyblish.starter.instance`   | Unit of outgoing data    | `Strange_model_default`

<br>

[ver]: https://cloud.githubusercontent.com/assets/2152766/18576835/f6b80574-7bdc-11e6-8237-1227f779815a.png
[ast]: https://cloud.githubusercontent.com/assets/2152766/18576836/f6ca19e4-7bdc-11e6-9ef8-3614474c58bb.png
[rep]: https://cloud.githubusercontent.com/assets/2152766/18759916/b2e3161c-80f6-11e6-9e0a-c959d63047a8.png
[for]: https://cloud.githubusercontent.com/assets/2152766/18759918/b479168e-80f6-11e6-8d1c-aee4e654d335.png
[pro]: https://cloud.githubusercontent.com/assets/2152766/18760901/d6bf24b4-80fa-11e6-8880-7a0e927c8c27.png
[usr]: https://cloud.githubusercontent.com/assets/2152766/18808940/eee150bc-8267-11e6-862f-a31e38d417af.png
[shd]: https://cloud.githubusercontent.com/assets/2152766/18808939/eeded22e-8267-11e6-9fcb-150208d55764.png

<br>
<br>

### Starter API

pyblish-starter provides a stateful API. State is set and modified by calling `pyblish_starter.install()`.
The following members are available via `pyblish_starter`.

| Member                          | Returns  | Description
|:--------------------------------|:---------|:--------
| `install(host)`                 | `str`    | Install Starter into the current interpreter session
| `uninstall()`                   | `str`    | Revert installation
| `ls()`                          | `dict`   | List available assets, relative `root`
| `root()`                        | `str`    | Absolute path to current working directory
| `format_user_dir(root, name)`   | `str`    | Return absolute path or user directory relative arguments
| `format_shared_dir(root)`       | `str`    | Return absolute path of shared directory
| `format_version(version)`       | `str`    | Return file-system compatible string of `version`
| `find_latest_version(versions)` | `int`    | Given a series of string-formatted versions, return the latest one
| `parse_version(version)`        | `str`    | Given an arbitrarily formatted string, return version number
| `register_root(root)`           |          | Register currently active root
| `register_host(host)`           |          | Register currently active host
| `register_plugins()`            |          | Register plug-ins bundled with Pyblish Starter
| `deregister_plugins()`          |          |
| `registered_host()`             | `module` | Return currently registered host

<br>

### Host API

A host must implement the following members.

| Member                    | Returns | Description
|:--------------------------|:--------|:--------
| `create(name, family)`    | `dict`  | Build fixture for outgoing data (see [instance]())
| `load(asset, version=-1)` | `str`   | Import external data into [container]()

<br>
<br>

### Information Hierarchy

The mental and physical model for files and folders look like this.

```bash
 ________________________________ ________________________________ 
|          |          |          |          |          |          |
| version1 | version2 | version3 | version1 | version2 | version3 |
|__________|__________|__________|__________|__________|__________|
|                                |                                |
|             asset1             |             asset2             |
|________________________________|________________________________|

```

<br>
<br>

### Contract

![](http://placehold.it/880x300)

Starter defines these families.

| Family              | Definition                                     | Link
|:--------------------|:-----------------------------------------------|:------------
| `starter.model`     | Geometry with deformable topology              | [Spec](#startermodel)
| `starter.rig`       | An articulated `starter.model` for animators   | [Spec](#starterrig)
| `starter.animation` | Pointcached `starter.rig` for rendering        | [Spec](#starteranimation)

<br>

### `starter.model`

![](http://placehold.it/880x100)

<img align="right" src="https://cloud.githubusercontent.com/assets/2152766/18526694/7453567a-7ab9-11e6-817c-84a874092399.png"></img>

A generic representation of geometry.

![aud][] **Target Audience**

- Texturing
- Rigging
- Final render

![req][] **Requirements**

- All DAG nodes must be parented to a single top-level transform
- Static geometry (no deformers, generators) `*`
- One shape per transform `*`
- Zero transforms and pivots `*`
- No intermediate shapes `*`
- UVs within 0-1 with full coverage, no overlap `*`
- Unlocked normals `*`
- Manifold geometry `*`
- No edges with zero length `*`
- No faces with zero area `*`
- No self-intersections `*`

![dat][] **Data**

- `label (str, optional)`: Pretty printed name in graphical user interfaces

![set][] **Sets**

- `geometry_SEL (geometry)`: Meshes suitable for rigging
- `aux_SEL (any, optional)`: Auxilliary meshes for e.g. fast preview, collision geometry

<br>
<br>

### `starter.rig`

![](http://placehold.it/880x100)

<img align="right" src="https://cloud.githubusercontent.com/assets/2152766/18526730/9c7f040a-7ab9-11e6-9007-4795ddbadde8.png"></img>

The `starter.rig` contains the necessary implementation and interface for animators to animate. 

![aud][] **Target Audience**

- Animation

![req][] **Requirements**

- All DAG nodes must be parented to a single top-level transform
- Must contain an `objectSet` for controls and cachable geometry
- Channels in `controls_SEL` at *default* values`*`
- No input connection to animatable channel in `controls_SEL` `*`
- [No self-intersections on workout](#workout) `*`

![dat][] **Data**

- `label (str, optional)`: Pretty printed name in graphical user interfaces

![set][] **Sets**

- `cache_SEL (geometry)`: Meshes suitable for pointcaching from animation
- `controls_SEL (transforms)`: All animatable controls
- `resources_SEL (any, optional)`: Nodes that reference an external file

<br>
<br>

### `starter.animation`

![](http://placehold.it/880x100)

<img align="right" src="https://cloud.githubusercontent.com/assets/2152766/18526738/a0fba5ba-7ab9-11e6-934f-48ca2a2ce3d2.png"></img>

Point positions and normals represented as one Alembic file.

![aud][] **Target Audience**

- Lighting
- FX
- Cloth
- Hair

![req][] **Requirements**

- [No infinite velocity](#extreme-acceleration) `*`
- [No immediate acceleration](#extreme-acceleration) `*`
- [No self-intersections](#self-intersections) `*`
- No sub-frame keys `*`
- [Edge angles > 30 degrees on elastic surfaces](#extreme-surface-tangency) `*`
- [Edge lengths within 50-150% for elastic surfaces](#extreme-surface-stretch-or-compression) `*`
- [Edge lengths within 90-110% for rigid surfaces](#extreme-surface-stretch-or-compression) `*`

![dat][] **Data**

- `label (str, optional)`: Pretty printed name in graphical user interfaces

![set][] **Sets**

- None

<br>

**Legend**

|          | Title               | Description
|:---------|:--------------------|:-----------
| ![aud][] | **Target Audience** | Who is the end result of this family intended for?
| ![req][] | **Requirements**    | What is expected of this asset before it passes the tests?
| ![dat][] | **Data**            | End-user configurable options
| ![set][] | **Sets**            | Collection of specific items for publishing or use further down the pipeline.
|          | `*`                 | Todo


[set]: https://cloud.githubusercontent.com/assets/2152766/18576835/f6b80574-7bdc-11e6-8237-1227f779815a.png
[dat]: https://cloud.githubusercontent.com/assets/2152766/18576836/f6ca19e4-7bdc-11e6-9ef8-3614474c58bb.png
[req]: https://cloud.githubusercontent.com/assets/2152766/18576838/f6da783e-7bdc-11e6-9935-78e1a6438e44.png
[aud]: https://cloud.githubusercontent.com/assets/2152766/18576837/f6d9c970-7bdc-11e6-8899-6eb8686b4173.png

<br>
<br>

### Example

The following is an example of the minimal effort required to produce film with Starter and Autodesk Maya.

**Table of contents**

- [Setup](#setup)
- [Model](#model)
- [Rigging](#rigging)
- [Animation](#animation)

<br>

##### Setup

Before any work can be done, you must install Starter.

```python
from pyblish_starter import install, maya
install(maya)
```

<br>

##### Modeling

Create a new model from scratch and publish it.

```python
from maya import cmds

cmds.file(new=True, force=True)

cmds.polyCube(name="Paul")
cmds.group(name="model")
instance = cmds.sets(name="Paul_model")

data = {
    "id": "pyblish.starter.instance",
    "family": "starter.model"
}

for key, value in data.items():
    cmds.addAttr(instance, longName=key, dataType="string")
    cmds.setAttr(instance + "." + key, value, type="string")

from pyblish import util
util.publish()
```

<br>

##### Rigging

Build upon the model from the previous example to produce a rig.

```python
import os
from maya import cmds
from pyblish_starter.maya import (
    hierarchy_from_string,
    outmesh,
    load
)

cmds.file(new=True, force=True)

# Load external asset
reference = load("Paul_model", namespace="Paul_")
nodes = cmds.referenceQuery(reference, nodes=True)
model_assembly = cmds.listRelatives(nodes[0], children=True)[0]
model_geometry = outmesh(cmds.listRelatives(
    model_assembly, shapes=True)[0], name="Model")

assembly = hierarchy_from_string("""\
rig
    implementation
        input
        geometry
        skeleton
    interface
        controls
        preview
""")

# Rig
control = cmds.circle(name="Control")[0]
skeleton = cmds.joint(name="Skeleton")
preview = outmesh(model, name="Preview")
cmds.skinCluster(model, skeleton)
cmds.parentConstraint(control, skeleton)

# Sets
sets = list()
sets.append(cmds.sets(control, name="all_controls"))
sets.append(cmds.sets(model, name="all_cachable"))
sets.append(cmds.sets(reference, name="all_resources"))

# Organise
cmds.parent(input_, "input")
cmds.parent(control, "controls")
cmds.parent(skeleton, "skeleton")
cmds.parent(model, "geometry")
cmds.parent(preview, "interface|preview")
cmds.setAttr(control + ".overrideEnabled", True)
cmds.setAttr(control + ".overrideColor", 18)
cmds.hide("implementation")
cmds.select(deselect=True)

# Create instance
instance = cmds.sets([assembly] + sets, name="Paul_rig")

data = {
    "id": "pyblish.starter.instance",
    "family": "starter.rig"
}

for key, value in data.items():
    cmds.addAttr(instance, longName=key, dataType="string")
    cmds.setAttr(instance + "." + key, value, type="string")

from pyblish import util
util.publish()
```

<br>

##### Animation

Build upon the previous example by referencing and producing an animation from the rig.

```python
from maya import cmds
from pyblish_starter.maya import (
    load,
    create
)

cmds.file(new=True, force=True)
cmds.playbackOptions(animationStartTime=1001, maxTime=1050)

# Load external asset
reference = load("Paul_rig", namespace="Paul01_")
nodes = cmds.referenceQuery(reference, nodes=True)

# Animate
all_controls = next(ctrl for ctrl in nodes if "all_controls" in ctrl)
control = cmds.sets(all_controls, query=True)[0]

keys = [
    (1001, 0),
    (1025, 10),
    (1050, 0)
]

for time, value in keys:
    cmds.setKeyframe(control,
                     attribute="translateY",
                     value=value,
                     time=time,
                     inTangentType="flat",
                     outTangentType="flat")

# Create instance
all_cachable = next(ctrl for ctrl in nodes if "all_cachable" in ctrl)
cmds.select(cmds.sets(all_cachable, query=True))

instance = cmds.sets(name="Paul_animation")

data = {
    "id": "pyblish.starter.instance",
    "family": "starter.animation"
}

for key, value in data.items():
    cmds.addAttr(instance, longName=key, dataType="string")
    cmds.setAttr(instance + "." + key, value, type="string")

from pyblish import util
util.publish()
```

<br>
<br>

#### Requirements specification

The following is a details description of each requirement along with motivation and technical reasoning for their existence.

<br>

##### Workout

A workout is an animation clip associated with one or more character rigs. It contains both subtle and extreme poses along with corresponding transitions between them to thoroughly exercise the capabilities of a rig.

The workout is useful to both the character setup artist, the simulation artist and automated testing to visualise overall performance and behavior and to discover problems in unforeseen corner cases.

<br>

##### Self-intersections

Three dimensional geometric surfaces inherently share no concept of volume or mass, but both realism and subsequent physical simulations, such as clothing or hair, depend on it.

> Implementation tip: A toon shader provides an option to produce a nurbs curve or mesh from self-intersecting geometry. A plug-in could take advantage of this to test the existence of such a mesh either at standstill or in motion.

<br>

##### Extreme Acceleration

In reality, nothing is immediate. Even light takes time to travel from one point to another. For realism and post-processing of character animation, such as clothing and hair, care must be taken not to exceed realistic boundaries that may complicate the physical simulation of these materials.

<br>


##### Extreme Surface Tangency

In photo-realistic character animation, when the angle between two edges exceeds 120 degrees, an infinitely sharp angle appears that complicates life for artists relying on this surface for collisions.

To work around situations where the overall shape must exceed 120 degrees - such as in the elbow or back of a knee - use two or more edges. The sum of each edges contribute to well beyond 360 degrees and may be as short as is necessary.

<br>

##### Extreme Surface Stretch or Compression

Surface stretch and compression on elastic surfaces may negatively affect textures and overall realism.
