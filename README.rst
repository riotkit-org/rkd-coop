Snippet Cooperative (RKD-COOP)
==============================

.. image:: ./docs/rkd-coop-technology-stack.png

Sharing snippets, plugins, packages never was so easy. :code:`rkd-coop` is a GIT-based tool similar to package manager that have repositories on GIT/Github!
Uses popular and easy JINJA2 templating to render configuration files based on answers asked to the user during snippet installation.

**Perfect tool to:**

- Share ready-to-use, customizable configuration files
- Share docker-compose.yml definitions where you can parametrize database credentials, container names
- Install plugins to any application, it just unpack files from repository and runs an installer script that is highly customizable

.. code:: bash

    export REPOSITORIES=https://github.com/riotkit-org/riotkit-harbor-snippet-cooperative
    rkd-coop :cooperative:sync          # similar to apt update, huh?
    rkd-coop :cooperative:install redis


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
