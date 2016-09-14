### Pyblish Starter

Jumpstart your publishing pipeline with a basic configuration.

<br>
<br>
<br>

### Features

- Basic discovery of assets
- Basic validation
- Model, rig and animation extraction

<br>
<br>
<br>

### Install

Starter takes the form of a Python package with embedded plug-ins.

```bash
$ pip install pyblish-starter
```

<br>
<br>
<br>

### Usage

Plug-ins are registered by calling `setup()`.

```python
>>> import pyblish_starter
>>> pyblish_starter.setup()
```

### Example

Scripted demonstration of how to model, rig and animate an asset.

<br>
<br>
<br>

### Contract

Starter defines these families.

| Family              | Definition                                    | Link
|:--------------------|:----------------------------------------------|:------------
| `starter.model`     | Geometry with deformable topology             | [Spec](#startermodel)
| `starter.rig`       | An articulated `starter.model` for animators  | [Spec](#starterrig)
| `starter.animation` | Pointcached `starter.rig` for lighting        | [Spec](#starteranimation)

<br>

### `starter.model`

<img align="right" src="https://cloud.githubusercontent.com/assets/2152766/18501858/3c85ab26-7a4b-11e6-8d09-8420a68f16b8.png"></img>

A generic representation of geometry.

```yaml
Instance:
  label (str, optional): Pretty printed name
  						 in graphical user interfaces

Sets:
  geometry_SEL: Meshes suitable for rigging
  aux_SEL: Auxilliary meshes for e.g. fast
  		   preview, collision geometry
```

<br>
<br>

### `starter.rig`

<img align="right" src="https://cloud.githubusercontent.com/assets/2152766/18501865/484fe1a6-7a4b-11e6-9157-ce1275fe86ea.png"></img>

The `starter.rig` contains the necessary implementation and interface for animators to produce 

```yaml
Instance:
  label (str, optional): Pretty printed name
  						 in graphical user interfaces

Sets:
  cache_SEL: Meshes suitable for
  			 pointcaching from animation
  controls_SEL: All animatable controls
  resources_SEL: Nodes that reference an external file
```

<br>

### `starter.animation`

<img align="right" src="https://cloud.githubusercontent.com/assets/2152766/18502081/d027e1cc-7a4c-11e6-8c01-baba21faabbe.png"></img>

Point positions and normals represented as one Alembic file.

```yaml
Instance:
  label (str, optional): Pretty printed name
  						 in graphical user interfaces

Sets:
  None
```

<br>
<br>
<br>

#### Todo

Instances, in particular the Animation instance, requires some setup before being cachable. We don't want the user to perform this setup, but rather a tool. The tool could be in the form of a GUI that guides a user through selecting the appropriate nodes. Ideally the tools would be implicit in the loading of an asset through an asset library of sorts.

- Tool to create model, rig and animation instance.