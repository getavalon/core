# Contribution Guidelines

Hi and welcome to Avalon! Here are some guidelines for how you can help advance the project.

<br>

### Feature Request

If you have an idea for a new or missing feature, you can submit a GitHub issue with the following ingredients.

| # |          | Description
|--|:---------|:-
| 1 | **Goal** | In one sentence, what is the purpose of the feature?
| 2 | **Motivation** | Why does it need to exist? What made you think of it? Feel free to elaborate, the more we understand the more able we will be to figure out the best solution, or point towards an existing (but not so visible) solution.
| 3 | **Implementation** | Optional. Got an idea of how to implement it, but would like to talk about it first? This is a great place to do just that.

**But First**

1. [Search](https://github.com/getavalon/core/issues) for whether the feature you seek has already been requested and/or implemented
1. [Ask](https://gitter.im/getavalon/Lobby) whether what you seek to do can be done.

**Examples**

- [#385](https://github.com/getavalon/core/issues/385)
- [#390](https://github.com/getavalon/core/issues/390)
- [#415](https://github.com/getavalon/core/issues/415)

<br>

### Bug

When you run into bugs, you can submit an issue. In order for it to be resolved quickly, a bug report should contain:

| # |          | Description
|--|:---------|:-
| 1 | **Problem** | What happened? Keep it short
| 2 | **Reproducible** | How can someone else encounter the bug? Keep it minimal
| 3 | **Attempts** | What have you tried so far?
| 4 | **Solution** | Optional. If you've got an idea of what to do about it, but would like to talk about it before diving into code, here's your chance

It's hard to make an exact checklist out of these, as it depends on the particular bug. 

**Examples**

- [#389](https://github.com/getavalon/core/issues/389)
- [#377](https://github.com/getavalon/core/issues/377)
- [#412](https://github.com/getavalon/core/issues/412)

<br>

### Pull Request

Here's a few things to keep in mind as you contribute code to Avalon. The overall goal is getting code merged as quickly as possible. Ambiguity cause delays, treat written English as code; it should be clear and concise. 

1. Every new line of code needs purpose and motivation, preferably in the shape of an issue, alternatively as a linked topic in chat. The goal is giving future developers (ourselves included) an understanding of why something was done the way that it was.
1. Every removed line of code needs a reason; but if you do manage to remove code without breaking things, you're a star and most welcome to contribute.

**Description**

When you present your PR, here's what you need to do.

1. Briefly summarise the changes, everybody loves bullet lists
1. Refer to a related issue, if one exists. Else, make one, and refer to [Feature Request](#feature-request) above.
2. Adhere to code quality standards

**Code Quality**

Here are a few things to keep in mind with regards to code quality.

| # |          | Description
|--|:---------|:-
| 1A | **Minimal indirection** | In order to cope with the cognitive overhead of traversing code, keep relevant code together.
| 1B | **Only separate what is shared** | If a function is only ever used by one module, it should become part of that module. Likewise for modules used by a package.
| 1C | **Prefer fewer large modules to many small** | Whenever you import a module, you create a dependency. The less of those there are, the better. That means no modules with just a single class.
| 1D | **Upward and lateral imports** | A module may reach up and sideways in the package hierarchy, but not down. E.g. `avalon/maya/lib.py` may reach `avalon/io.py`, but `io.py` may not reach into `maya`.
| 1E | **Shallow dependency tree** | Avoid traversing more than 3 levels anywhere, unless there is good reason. 3 is plenty.
| 1F | **Group by dependency, not type** | That is, if 6 modules share code, they should share a package. If 12 functions are used by a single module, they should be part of that module.
| 2A | **Namespaces are good** | Do not duplicate namespaces, e.g. `avalon.gui.models.model_subset` where "model" appears twice.
| 2B | **Namespaces are good** | Do not import functions or classes, import modules and keep their namespace. E.g. `QtWidgets.QPushButton` is better than `QPushButton`.
| 2C | **Namespaces are good** | Do not consolidate multiple modules into one, with the exception of `api.py`. Doing so makes it difficult to understand where things come from and where to look for them. `api.py` is different because it is the API; users are not supposed to know where code resides internally as that is implementation detail.

**Examples**

- **Bad**: https://github.com/getavalon/core/pull/414, vague, subjective
- **Good**: https://github.com/getavalon/core/pull/400, minimal, clear goal
- **Bad**: https://github.com/getavalon/core/pull/413, no motivation, no goal
- **Good**: https://github.com/getavalon/core/pull/403, minimal, clear goal