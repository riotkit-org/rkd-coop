Snippet Cooperative
===================

Have you ever tried to implement a plugin repository & installing mechanism? It's not easy, and we know it.
RKD Snippet Cooperative is a ready-to-use mechanism that works with ANY programming language, but still you need to have installed Python 3 and PIP.

How it works?
-------------

The mechanism is using GIT repository as a central repository of content, there is a command to synchronize all repositories :code:`rkd-coop :cooperative:sync`.
With :code:`rkd-coop :cooperative:install NAME` a snippet can be installed from local repository.

Snippet structure - custom installation process
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Snippets structure allows to define custom installers per snippet - by using RKD each snippet have a possibility to override tasks :code:`:snippet:wizard` and :code:`:snippet:install`.

To overwrite the files copying process simply implement a task :code:`:snippet:install`


Snippet structure - interactive installation wizard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The :code:`:snippet:wizard` task is intended to implement an interactive Wizard, it should be overridden by snippet's makefile.yaml

Simplicity over complexity
--------------------------

Snippet cooperative is not an application store, or a package manager.
It is intended to be a simple snippet store, but we do not exclude implementation of "store-like" mechanism in the future.
