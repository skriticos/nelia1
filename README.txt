
General code navigation

- All document data and cross-module runtime data is handled by the datastore
  module. An instance is imported in each module as global variable "data".

- The currently active project is determined by the selection on the project
  widget and is used through the other widgets. This can be aquired with
  data.spid. The associated persistent project datastructure can be accessed via
  data.spro.

- All the core views of the GUI module controls (project, log, roadmap) are
  simply called "view" and the associated models "model" within the module.


