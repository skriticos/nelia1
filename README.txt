
TABLE OF CONTENTS

C0 ~ META
C1 ~ COMMON FUNCTIONS
C2 ~ DATA EXCHANGE AND STORAGE
C3 ~ GUI CONTROL MODULES
C4 ~ PROJECT MODULE
C5 ~ LOG MODULE
C6 ~ ROADMAP MODULE


C0 ~ META

   Each source file sholud start with a sensible overview of what the functions
   and classes in the file are doing. Then they should import all required
   standard library modules, PySide modules (* notation is ok, as Qt comes with
   a strict naming scheme) and finally the application modules used by the
   current file.


C1 ~ COMMON FUNCTIONS

   Common functions are declared in the src/common.py file and contain functions
   and decorators used through the entire codebase.

   Logging functions:

      log(msg): function is the lowest level of the logging functions. It adds a
      timestamp to the log message and sends it to the log target, usually
      stdout.

      logMarker(): funciton is used to mark logstream locations. This is mostly
      used interactively during development testing before performing an action.
      It dumps a visible marker into the logstream.

      @logger(declaration, *argnames): decorator is used by *all* functions and
      class methods in the project (except log and logMarker). It is used to log
      the call history and parameters that are passed. These decorators *should*
      be removed for production code, though just returning from the log method
      would also do with a performance penalty.

   State functions:

      applyState(states, widget): function takes a set of states and a target
      widget as arguments and appies the states to the target widget. States are
      generally defined in the beginning of GUI control modules.

   Conversion functions:

      convert(item): function takes an item argument and depending on the type
      and value converts into a target value. If item is an integer, it converts
      it to a datetime string for display in the tables. If it's one of the Qt
      table sort order string declarations, it converts them to instances
      (reqired to make serialization work). Otherwise it raises an exception.
      Using this function with improper items results in bugs, some of which can
      be silent (e.g. non-datetime integer parameter).


C2 ~ DATA EXCHANGE AND STORAGE

   Data exchange and storage functions are declared in the src/datacore.py file.
   The datacore is a global data tree that stores all document, configuration
   and shared runtime data. It's used by importing the dc instance in the file
   and then addressing data with a dot notation dc.s.modulename.valuename.v.
   The tree can be nested with no fixed boundaries. e.g. dc.a.b.c.d.e.f.v would
   be completely valid despite lacking any clue on what it's supposed to be.
   There are a few purpose subtrees:

      s: storage. Anything that is done in the dc.s.* tree is considered part of
      the current document and is stored on saving.

      c: configuration. Anything that is done in the dc.c.* tree is considered
      part of the *global* configuration and is saved to a global appliaction
      configuration file (~/.config/<appname>/<appname>.config)

      x: informal, generic runtime data

      ui: user interface handles (e.g. dc.ui.project.v is reference to the
      project widget)

      m: module references (e.g. dc.m.project.v is a reference to the project
      gui control module)

   Other namespaces are not strictly declared, but are used in some situations,
   like dc.spid.v (selected project pid, runtime). All non-local data is stored
   in the datacore and some local too.

   There are a few utility functions in the datacore module:

   dc(save)|(load) -> save/load document
   dc(save)|(load)config -> save / load configuration


C3 ~ GUI CONTROL MODULES

   This section details the commonalities of the GUI control modules. For
   specifics, see the detailing sections below.

   GUI control modules are the backend to widgets. They implement the
   functionility behind the GUI controls and glue them together with callbacks.
   They also define module states that are applied based on the situation.

   states:

      States are groupings of widget attributes. For instance, at startup there
      are a set of GUI controls that are disabled (like delete project or
      navigate to the log page). These states are applied with the applyStates
      function from the common module. They *must* be part of a local class
      named 'states'. All these states are described in a dictionary and should
      be added with no identation. E.g. class states: pass .. states.<statename>
      = {..}.

   callback controls:

      These have the pattern (enable)|(disable)${group name}Callbacks()
      They enable/disable callback groups.

   callback implementations:

      These have the pattern on${callback name}${action type}()
      They implement the callbacks that occur and are non-core to the module.
      This last part is important. If it's a callback that requires the change
      of a document data segment, it's in the main class of the module. If it's
      a simple state change, navigation or similar, it's in the preface.

   utility classes:

      Classes that are core part of the GUI control, but are so complex that a
      separation is justified. The table controls are in this category. These
      have lower case names and only use static methods.

   core classes:

      These perform the document data manipulation activities. They start with
      Nx* and use dynamic methods. If you are interested in what the module is
      actually doing without all the noise, check the Nx* classes.


C4 ~ PROJECT MODULE




C5 ~ LOG MODULE


C6 ~ ROADMAP MODULE




