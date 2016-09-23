### Pyblish Starter

A basic asset creation pipeline, with batteries included.

> WARNING: Not ready for use.

**Table of contents**

- [Install](#install)
- [Usage](#usage)
- [Description](#description)
- [Terminology](#terminology)
- [Information Hierarchy](#information-hierarchy)
- [Contract](#contract)
    - [`starter.model`](#startermodel)
    - [`starter.rig`](#starterrig)
    - [`starter.animation`](#starteranimation)

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

From here, you model, rig and animate as per the contract below.

<br>
<br>

### Description

Build your own asset creation pipeline, starting with the basics.

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

### Terminology

Starter reserves the following words for private and public use. Public members are exposed to the user, private ones are internal to the implementation.

|          | Term                | Public | Description         | Example
|:---------|:--------------------|:-------|:--------------------|:------------------------
| ![][pro] | `project`           | `X`    | Root of information | Gravity, Dr. Strange
| ![][ast] | `asset`             | `X`    | Unit of data        | Ryan, Bicycle, Flower pot
| ![][ver] | `version`           | `X`    | An asset iteration  | v1, v034
| ![][rep] | `representation`    |        | A data format       | Maya file, pointcache, thumbnail
| ![][for] | `format`            |        | A file extension    | `.ma`, `.abc`, `.ico`, `.png`
| ![][for] | `public`            |        | Shared data         | v034 of Ryan
| ![][for] | `private`           |        | User data           | Scenefile for v034 of Ryan

[ver]: https://cloud.githubusercontent.com/assets/2152766/18576835/f6b80574-7bdc-11e6-8237-1227f779815a.png
[ast]: https://cloud.githubusercontent.com/assets/2152766/18576836/f6ca19e4-7bdc-11e6-9ef8-3614474c58bb.png
[rep]: https://cloud.githubusercontent.com/assets/2152766/18759916/b2e3161c-80f6-11e6-9e0a-c959d63047a8.png
[for]: https://cloud.githubusercontent.com/assets/2152766/18759918/b479168e-80f6-11e6-8d1c-aee4e654d335.png
[pro]: https://cloud.githubusercontent.com/assets/2152766/18760901/d6bf24b4-80fa-11e6-8880-7a0e927c8c27.png

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

| Family              | Definition                                                  | Link
|:--------------------|:------------------------------------------------------------|:------------
| `starter.model`     | Geometry with deformable topology                           | [Spec](#startermodel)
| `starter.rig`       | An articulated `starter.model` for animators                | [Spec](#starterrig)
| `starter.animation` | Pointcached `starter.rig` for tech-anim and lighting        | [Spec](#starteranimation)

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

The `starter.rig` contains the necessary implementation and interface for animators to produce 

![aud][] **Target Audience**

- Animation

![req][] **Requirements**

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

Before any work can be done, you must initialise Starter.

```python
# Prerequisite
import pyblish_maya
pyblish_maya.setup()

# Starter
import pyblish_starter
pyblish_starter.setup()
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
