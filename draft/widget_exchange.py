# SNIPPET

self.roadmap.gridLayout_2.removeWidget(self.roadmap.rmap_push_milestone)
self.roadmap.rmap_push_milestone.close()

# create new widget
# self.roadmap.rmap_push_milestone = MPushButton(self.roadmap, x, y, versions)
# rinse and repeat for other widgets

self.roadmap.gridLayout_2.addWidget(
    self.roadmap.rmap_push_milestone, 0, 1, 1, 1)
self.roadmap.label_2.setBuddy(self.roadmap.rmap_push_milestone)

# SNIPPET

