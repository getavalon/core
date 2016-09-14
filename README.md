### Pyblish Starter

Jumpstart your publishing pipeline with a basic configuration.

> WARNING: This is in development (see latest commit date) and is NOT YET ready for an audience

<br>
<br>

### Features

- Asset definition template
- Versioning

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

Plug-ins are registered by calling `setup()`.

```python
>>> import pyblish_starter
>>> pyblish_starter.setup()
```

<br>
<br>

### Contract

Starter defines these families.

| Family              | Definition                                                  | Link
|:--------------------|:------------------------------------------------------------|:------------
| `starter.model`     | Geometry with deformable topology                           | [Spec](#startermodel)
| `starter.rig`       | An articulated `starter.model` for animators                | [Spec](#starterrig)
| `starter.animation` | Pointcached `starter.rig` for tech-anim and lighting        | [Spec](#starteranimation)

<br>

### `starter.model`

<img align="right" src="https://cloud.githubusercontent.com/assets/2152766/18526694/7453567a-7ab9-11e6-817c-84a874092399.png"></img>

A generic representation of geometry.

**Target Audience**

- Texturing
- Rigging
- Final render

**Requirements**

- Static geometry (no deformers, generators)
- One shape per transform `*`
- Zero transforms and pivots `*`
- No intermediate shapes `*`
- UVs within 0-1 with full coverage, no overlap `*`
- Unlocked normals `*`
- Manifold geometry `*`
- No edges with zero length `*`
- No faces with zero area `*`
- No self-intersections `*`

> `*` = Todo

**Data**

- `label (str, optional)`: Pretty printed name in graphical user interfaces

**Sets**

- `geometry_SEL (geometry)`: Meshes suitable for rigging
- `aux_SEL (any, optional)`: Auxilliary meshes for e.g. fast preview, collision geometry

<br>
<br>

### `starter.rig`

<img align="right" src="https://cloud.githubusercontent.com/assets/2152766/18526730/9c7f040a-7ab9-11e6-9007-4795ddbadde8.png"></img>

The `starter.rig` contains the necessary implementation and interface for animators to produce 

**Requirements**

- Channels in `controls_SEL` at *default* values`*`
- No input connection to animatable channel in `controls_SEL` `*`
- [No self-intersections on workout](#workout) `*`

**Data**

- `label (str, optional)`: Pretty printed name in graphical user interfaces

**Sets**

- `cache_SEL (geometry)`: Meshes suitable for pointcaching from animation
- `controls_SEL (transforms)`: All animatable controls
- `resources_SEL (any, optional)`: Nodes that reference an external file

<br>
<br>

### `starter.animation`

<img align="right" src="https://cloud.githubusercontent.com/assets/2152766/18526738/a0fba5ba-7ab9-11e6-934f-48ca2a2ce3d2.png"></img>

Point positions and normals represented as one Alembic file.

**Requirements**

- [No infinite velocity](#extreme-acceleration) `*`
- [No immediate acceleration](#extreme-acceleration) `*`
- [No self-intersections](#self-intersections) `*`
- No sub-frame keys `*`
- [Edge angles within -120 to 120 degrees on elastic surfaces](#extreme-surface-tangency) `*`
- [Edge lengths within 50-150% for elastic surfaces](#extreme-surface-stretch-or-compression) `*`
- [Edge lengths within 90-110% for rigid surfaces](#extreme-surface-stretch-or-compression) `*`

**Data**

- `label (str, optional)`: Pretty printed name in graphical user interfaces

**Sets**

- None

<br>

**Legend**

| Title               | Description
|:--------------------|:-----------
| **Target Audience** | Who is the end result of this family intended for?
| **Requirements**    | What is expected of this asset before it passes the tests?
| **Data**            | End-user configurable options
| **Sets**            | Collection of specific items for publishing or use further down the pipeline.

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

```python
from maya import cmds

cmds.file(new=True, force=True)

cmds.polyCube(name="Paul")
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

```python
import os
from maya import cmds
from pyblish_starter.maya import hierarchy_from_string

cmds.file(new=True, force=True)

asset = os.path.join(
    "public",
    "Paul_model",
    "v001",
    "Paul_model.ma"
)

# Load external asset
cmds.file(asset, reference=True, namespace="model_")
reference = cmds.file(asset, query=True, referenceNode=True)
nodes = cmds.referenceQuery(reference, nodes=True)
geometry = cmds.ls(nodes, assemblies=True)

hierarchy_from_string("""\
rig
    implementation
        geometry
        skeleton
    interface
        controls
        preview
""")

# Build
control = cmds.circle(name="Control")[0]
skeleton = cmds.joint(name="Skeleton")
preview = cmds.createNode("mesh")
cmds.connectAttr(geometry[0] + ".outMesh", preview + ".inMesh")
preview = cmds.listRelatives(preview, parent=True)[0]
preview = cmds.rename(preview, "preview")

# Organise
cmds.parent(control, "controls")
cmds.parent(skeleton, "skeleton")
cmds.parent(geometry, "geometry")
cmds.parent(preview, "interface|preview")

# Setup
...
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

<br>
<br>

#### Todo

Instances, in particular the Animation instance, requires some setup before being cachable. We don't want the user to perform this setup, but rather a tool. The tool could be in the form of a GUI that guides a user through selecting the appropriate nodes. Ideally the tools would be implicit in the loading of an asset through an asset library of sorts.

- Tool to create model, rig and animation instance.
