This is a living document under continous improvement. It outlines a set of guidelines for the structure of a typical Avalon graphical user interface.

<br>

### Goal

Improve communication, maintenance and code quality.

<br>

### Example

Each of the below guidelines are implemented in the `convention` GUI.

```bash
python -m avalon.tools.convention \path\to\avalon-core\CONVENTION.md
```

![image](https://user-images.githubusercontent.com/2152766/63637288-edd15080-c672-11e9-8697-a7eba1690d57.png)

<br>

### Motivation

Our "tools" are GUIs written in Qt, and GUIs are a hard problem to solve. There is no PEP 008 for writing graphical applications, and the result is a lack of consistency and foresight.

- There's architecture - "MV", do we need it, how do we apply it effectively?
- There's structure - pages, panels, widgets and layouts; how do we structure those?
- There's reactivity - which signals should exist and how do we handle them?
- There's communication - which widgets should talk to which, and which should go through a controller?
- There's models - What are they, what are their responsibilities?
- There's responsiveness - Anything made asynchronous multiplies every problem by 10x
- There's division of labour - do we create 3 small GUIs that do one thing each well, or 1 GUI that does everything?

Without appropriate answers to these questions, extending or editing a graphical application is a problem made even harder.

<br>

### Implementation

Let's see if we can run through these and establish a foundation upon which to build GUIs effectively. I'll write these as unambious as I can, but remember these are guidelines and though some are tried and true, some are not (I'll tag these appropriately).

- [Naming Convention](#naming-convention)
- [Architecture](#architecture)
- Structure
	- [View](#structureii---view)
	- [Model](#structure-ii---model)
- [Responsiveness](#responsiveness)

<br>

#### Naming Convention

Python uses snake_case, Qt uses mixedCase; what do we do?

Clearly Qt is being naughty; forwarding the conventions from one language to another. But we can't ignore it, so what are our options?

1. [ ] Stand fast - Stick with snake_case where you can, mixedCase where you must
2. [ ] Give in - Use mixedCase everywhere
3. [x] Compromise - Use whichever convention is the majority of code per module or package

##### Stand Fast

This is what I typically do and see.

```py
from Qt import QtWidgets

class Window(QtWidgets.QDialog):
	def __init__(self, parent=None):
		super(Window, self).__init__(parent)

		my_button = QtWidgets.QPushButton("Press me")
		some_layout = QtWidgets.QHBoxLayout(self)
		some_layout.addWidget(my_button)

		my_button.clicked.connect(self.on_button_clicked)

	def mousePressEvent(self, event):
		pass

	def on_button_clicked(self):
		pass
```

Which is clearly horrendous. The few occasions where Qt appears to play ball - `clicked` and `connect` - are circumstantial. That isn't snake case, it's mixedCase masquerading as snake_case, ready to jump out at you at a moments notice.

One of the advantages (or so I tell myself) is that it's obvious which methods are overridden, and which are new. But is that enough to justify the overhead in reading ability? It's like reading-an ENGlish `_sen_tenc_e_` with 2 deffirent ConvenTions. Takes you out of the story.

#### Give in

Why not just write everything in mixedCase and get it over with?

If your code consists of only Qt and your own code, that's a fine idea; but standard and third-party libraries don't work that way.

```py
import pymongo

class Model(QtWidgets.QTableModel):
	def setData(self, index, value, role):
		item = pymongo.find_one({"type": "asset"})
		...
```

<br>

#### Compromise

Optimise to reduce context switching. Use the majority convention; less granularity is better.

1. Per project
1. Per package
2. Per module
3. Per class
3. Per method
3. Per block

For example, if a package (e.g. `avalon.loader`) is mostly Qt, use mixedCase. But if it isn't clear (e.g. `avalon.maya`) use mixedCase for modules where mixedCase is a majority, snake_case otherwise. If it isn't clear *within* a module which is a majority, stay consistent within a class, method or worst case, per block of code.

**Bad**

Sometimes you have no choice but to be consistent per block, but don't do this.

- Each line has its own convention
- One line has two conventions
- Context switch count: 4

```py
class Window(QtWidgets.QDialog):
	def __init__(self):
		some_button = QtWidgets.QPushButton("Hello")     # 1
		myLabel = QtWidgets.QLabel("World")              # 2
		this_layout = QtWidgets.QVBoxLayout(self)        # 3
		that_widget = QtWidgets.QWidget()                #
		otherLayout = QtWidgets.QHBoxLayout(that_widget) # 4
```

**Good**

Instead do this.

- Context switch count: 2

```py
class Window(QtWidgets.QDialog):
	def __init__(self):
		some_button = QtWidgets.QPushButton("Hello")    # 1
		this_layout = QtWidgets.QVBoxLayout(self)       #

		thatWidget = QtWidgets.QWidget()                # 2
		myLabel = QtWidgets.QLabel("World")             #
		otherLayout = QtWidgets.QHBoxLayout(thatWidget) #
```

That's 50% less context switching for the same code, however structural consistency is now worsened, as the layout initialisation is now spread across two blocks.

Structural consistency is more important than convention.

<br>

#### Architecture

You generally don't need to divide an application into model and view (MV) unless it is of a certain size. But as this is an article on consistency, let's move the goal posts to say "No application is small enough to not require MV".

With MV as our baseline, here's how to implement it.

| Module | Description
|:-------|:----
| `view.py` | The paintbrush. The "main" of our Window, the cortex of where all widgets come together. This is responsible for drawing to the screen and for converting user interaction to interactions with the "controller"
| `model.py` | The brain. The "main" of our program, independent of a view.

These three are all that is required to implement an application. Additional modules are for convenience and organisation only, such as..

| Module | Description
|:-------|:---------
| `widgets.py` | Independent widgets too large to fit in `view.py`, yet specific to an application (i.e. not shared with anything else)
| `util.py` | Like widgets, but non-graphical. Standalone timers, text processing, threading or delay functions.
| `delegates.py` | If relevant; these create a dependency between model and view, which typically only communicate through the controller.

<br>

#### Structure I - View

This involves the `def __init__()` in `view.py`, the remaining methods being signal and event handlers.

```py
class Window(QtWidgets.QMainWindow):
	title = "My Window"

    def __init__(self, model, parent=None):
    	super(Window, self).__init__(parent)
    	self.setWindowTitle(self.title)
        self.setWindowIcon(QtGui.QIcon(...))
        self.setAttribute(QtCore.Qt.WA_StyledBackground)

    	pages = {
    		"home": QtWidgets.QWidget(),
    	}

    	panels = {
    		"header": QtWidgets.QWidget(),
    		"body": QtWidgets.QWidget(),
    		"footer": QtWidgets.QWidget(),
    		"sidebar": QtWidgets.QWidget(),
    	}

    	widgets = {
    		"pages": QtWidgets.QStackedWidget(),
    		"logo": QtWidgets.QWidget(),
    		"okBtn": QtWidgets.QPushButton("Ok"),
    		"cancelBtn": QtWidgets.QPushButton("Cancel"),
    		"resetBtn": QtWidgets.QPushButton("Reset"),
    	}

    	icons = {
    		"cancelBtn": resources.icon("cancelBtn"),
    	}

```

**Notes**

- **S1** Widgets MUST are separated into `pages`, `panels` and `widgets`
	- Pages are the full screen of an application, except statusbar, docks, toolbar and menu. Most apps only have one page, but some - like Pyblish Lite and QML - have more
	- Panels are subdivisions of a Page
	- Widgets are self explanatory
- **S2** Widgets MUST be declared at the top
- **S3** Widgets MUST have a mixedCase name, used in CSS
- **S4** `Window` MUST have `title` declared as class attribute, used to dynamically change window title at run-time, e.g. to reflect a selection or state
- **S5** Like widgets, icons SHOULD be declared up-front
- **S6** Resource logic and I/O SHOULD be handled separately, for testing
- **S7** Object names SHOULD be mixedCase, to conform with JavaScript/CSS where they are used

```py
class Window(QtWidgets.QMainWindow):
	title = "My Window"

    def __init__(self, model, parent=None):
    	super(Window, self).__init__(parent)

		...

        for name, widget in itertools.chain(panels.items(),
                                            widgets.items(),
                                            pages.items()):
            # Expose to CSS
            widget.setObjectName(name)

        	# Support for CSS
            widget.setAttribute(QtCore.Qt.WA_StyledBackground)

        self.setCentralWidget(widgets["pages"])
        widgets["pages"].addWidget(pages["home"])

```

**Notes**

- **S10** Every widget MUST be given a unique name
- **S11** Every widget MUST be stylable with CSS
- **S12** Central widget MUST be a `QStackedWidget` to facilitate multiple pages 

```py
class Window(QtWidgets.QMainWindow):
	title = "My Window"

    def __init__(self, model, parent=None):
    	super(Window, self).__init__(parent)

    	...

    	layout = QtWidgets.QHBoxLayout(panels["header"])
    	layout.setContentsMargins(0, 0, 0, 0)
    	layout.setMargin(0)
    	layout.addWidget(widgets["logo"])

    	layout = QtWidgets.QHBoxLayout(panels["body"])
    	layout.setContentsMargins(0, 0, 0, 0)
    	layout.setMargin(0)
    	layout.addWidget(widgets["okBtn"])
    	layout.addWidget(widgets["cancelBtn"])
    	layout.addWidget(widgets["resetBtn"])

    	layout = QtWidgets.QHBoxLayout(panels["body"])
    	layout.setContentsMargins(0, 0, 0, 0)
    	layout.setMargin(0)
    	layout.addWidget(QtWidgets.QLabel("My Footer"))

    	#  ___________________
    	# |           |       |
    	# |___________|       |
    	# |			  | 	  |
    	# |___________|       |
    	# |           |       |
    	# |___________|_______|
    	#
    	layout = QtWidgets.QGridLayout(pages["home"])
    	layout.setContentsMargins(0, 0, 0, 0)
    	layout.addWidget(panels["header"], 0, 0)
    	layout.addWidget(panels["body"], 1, 0)
    	layout.addWidget(panels["footer"], 2, 0)
    	layout.addWidget(panels["sidebar"], 0, 1, 0, 2)
```

**Notes**

- **S20** Layouts MUST all be called `layout`; don't bother with unique names or maintaining reference to them
- **S21** All layouts MUST be populated together, in the same block
- **S22** Illustrations MAY be used to communicate intent and reduce cognitive load, especially for complex layouts

```py
class Window(QtWidgets.QMainWindow):
	title = "My Window"

    def __init__(self, model, parent=None):
    	super(Window, self).__init__(parent)

    	...

        widgets["logo"].setCursor(QtCore.Qt.PointingHandCursor)
        widgets["okBtn"].setTooltip("Press me")
        widgets["cancelBtn"].setTooltip("Don't press me")
        widgets["cancelBtn"].setIcon(icons["cancelIcon"])
        widgets["list"].setModel(model)

        widgets["okBtn"].clicked.connect(self.onOkClicked)
        widgets["list"].selectionChanged.connect(self.onSelectionChanged)
```

**Notes**

- **S30** Widgets MUST be initialised together, in the same block
- **S31** Widgets SHOULD be initialised in the order they were declared
- **S32** Signals MUST be initialised together, in the same block
- **S33** Signals MUST all have an `on_` prefix, they are *responding* to an event

```py
class Window(QtWidgets.QMainWindow):
	title = "My Window"

    def __init__(self, model, parent=None):
    	super(Window, self).__init__(parent)

    	...

    	self._pages = pages
    	self._panels = panels
    	self._widgets = widgets
    	self._model = model

    	self.setupA()
    	self.setupB()
    	self.updateC()

    	# Misc
    	# ...
```

**Notes**

- **S40** Private members MUST be declared together, after initialisation
- **S41** Post-initialisation MUST happen together

```py
class Window(QtWidgets.QMainWindow):
	title = "My Window"

    def __init__(self, model, parent=None):
    	super(Window, self).__init__(parent)

    	...

    def onThis(...):
    def onThat(...):
    def onThisChanged(...):
    def onThatChanged(...):
    ...
```

**Notes**

- **S50** All methods of a window SHOULD be signal handlers, there isn't much else for a window to do


```py
class Window(QtWidgets.QMainWindow):
	title = "My Window"

    def __init__(self, model, parent=None):
    	super(Window, self).__init__(parent)

    	...


class SmallHelperWidget(...):
	pass


class SpecialityButton(...):
	pass
```

**Notes**

- **S60** Single-use helper classes and functions for window SHOULD reside with window

<br>

#### Structure II - Model

A view merely interprets what the user wants, the model is what actually makes it happen. When a button is pressed, a signal handler calls on the model to take action.

```py
class View(Widget):
	...

	def onCopyClicked(self):
		index = self.currentIndex()
		self._model.copyFrom(index)
```

Likewise, when the model does something, the view is what tells the user about it.

```py
class Model(QtCore.QObject):
	stateChanged = QtCore.Signal(str)


class View(Widget):
	def __init__(self, model, parent=None):
		super(View, self).__init__(parent)

		...

		model.stateChanged.connect(self.onStateChanged)

	def onStateChanged(self, state):
		self._widgets["statusLabel"].setText(state)
```

- **S60** The model MAY operate freely, such as in response to IO, a timed event or signals from an external process or web request.
- **S61** The view MAY access the model
- **S62** The model MAY NOT access the view
- **S64** The model MAY be accessed by individual widgets. If you can, think of how QML allows this and how convenient and intuitive that is, without any apparent downside

<br>

#### Responsiveness

Always develop your application synchronously at first, blocking at every turn. Once a series of operations run stable but cause too much delay (200 ms+), consider parallelising and what should be happening from the users point of view.

1. What does the user need to know? E.g. progress bar, status message, email on completion. Your safest course of action is switching page to a "Loading Screen", then consider balancing between interactivity and information.
2. What is the user allowed to do? E.g. some buttons disabled, some actions able to operate in parallel. Your simplest course of action is to keep the GUI responsive, but disable all widgets. Then look for a balance between enabled and safe.
