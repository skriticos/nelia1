<map version="0.9.0">
<!-- To view this file, download free mind mapping software FreeMind from http://freemind.sourceforge.net -->
<node CREATED="1350733899133" ID="ID_1093274020" MODIFIED="1351067614956" TEXT="Nelia">
<node CREATED="1350734158119" ID="ID_1223778241" MODIFIED="1350734233980" POSITION="right" TEXT="root">
<node CREATED="1350734191501" ID="ID_1546356290" MODIFIED="1350734434833">
<richcontent TYPE="NODE"><html>
  <head>
    
  </head>
  <body>
    <p>
      <b>run.py </b>
    </p>
    <p>
      Launch the application (GUI)
    </p>
  </body>
</html></richcontent>
</node>
<node CREATED="1350734204657" ID="ID_1507332562" MODIFIED="1350734207411" TEXT="utils">
<node CREATED="1350734209347" ID="ID_1274978076" MODIFIED="1350916098214">
<richcontent TYPE="NODE"><html>
  <head>
    
  </head>
  <body>
    <p>
      <b>tablemodel.py </b>
    </p>
    <p>
      Create an item view model from
    </p>
    <p>
      a two dimensional python array
    </p>
  </body>
</html></richcontent>
</node>
</node>
</node>
<node CREATED="1350734445227" ID="ID_667339652" MODIFIED="1350734479130" POSITION="left" TEXT="status">
<node CREATED="1350734453626" ID="ID_827774791" MODIFIED="1351004533278">
<richcontent TYPE="NODE"><html>
  <head>
    
  </head>
  <body>
    <p>
      <b><font color="#ff0000">Next Steps</font></b>
    </p>
    <p>
      - add (version pattern), change, delete root entry
    </p>
    <p>
      - data persistence via pickle
    </p>
    <p>
      - create version primer
    </p>
  </body>
</html></richcontent>
</node>
<node CREATED="1350738940188" FOLDED="true" ID="ID_1036838821" MODIFIED="1350897555148" TEXT="imperatives">
<node CREATED="1350738946252" ID="ID_1231598678" MODIFIED="1350738995517" TEXT="flexible project design (i.e. roadmap, dependencies, additional utilities)"/>
</node>
<node CREATED="1350734468824" ID="ID_948458939" MODIFIED="1350734704190" TEXT="journal">
<node CREATED="1350734711158" FOLDED="true" ID="ID_1375500642" MODIFIED="1350916522691" TEXT="121020">
<node CREATED="1350734499384" ID="ID_372886409" MODIFIED="1350738932106">
<richcontent TYPE="NODE"><html>
  <head>
    
  </head>
  <body>
    <p>
      While starting with the application creation and the first mockups for the root table view, I discovered that creating a table model is a pain with the default pyside mapping. In consequence I have decided to create a helper module that will take a nested directory (with columns as keys for mapping) and create an appropriate item model from the dictionary. This will most likely be usefull for later table display elements.
    </p>
    <p>
      
    </p>
    <p>
      Anyway, so this is the first log entry and I should probably say something about the purpose for this entire project. The primary issue it's adressing is my difficulty to sort and track my projects.
    </p>
    <p>
      
    </p>
    <p>
      <b>Primary objective:</b>
    </p>
    <p>
      &quot;&quot;&quot; Create a tabular GUI tool to capture project ideas and track and log project progresses. &quot;&quot;&quot;
    </p>
    <p>
      &quot;&quot;&quot; Create a detailed page for each project which tracks the project objectives/features, journal, design, roadmap (dependencies) and issues. &quot;&quot;&quot;
    </p>
    <p>
      
    </p>
    <p>
      <b>Secondary objectives:</b>
    </p>
    <p>
      &quot;&quot;&quot; Add easily accessable test, build, deploy and source control (commit, sync) hooks (configurable GUI controls). &quot;&quot;&quot;
    </p>
    <p>
      &quot;&quot;&quot; Add general user and system configuration syncronisation. (e.g. set up packages on new OS installations and deploy personal configuration) &quot;&quot;&quot;
    </p>
    <p>
      
    </p>
    <p>
      <b>Tertiary objectives:</b>
    </p>
    <p>
      &quot;&quot;&quot; Create some utilities for PySide during the development. &quot;&quot;&quot;
    </p>
    <p>
      
    </p>
    <p>
      Syncing should happen with some kind of cloud service. As the primary target is Ubuntu, I'd say Ubuntu one would be a good choice (simple file sync).
    </p>
    <p>
      
    </p>
    <p>
      For the tooling, I have choosen pyqt / pyside (python3). The fast prototyping this seems to be a very good choice (no compile/run cycle) and gives me the power of the python data structures and dynamic typing (e.g. dictionaries).
    </p>
    <p>
      
    </p>
    <p>
      So, there you have it.
    </p>
  </body>
</html></richcontent>
</node>
</node>
<node CREATED="1350916411339" FOLDED="true" ID="ID_1976257918" MODIFIED="1351067599936" TEXT="121021">
<node CREATED="1350916423663" ID="ID_1985292984" MODIFIED="1350917521947">
<richcontent TYPE="NODE"><html>
  <head>
    
  </head>
  <body>
    <p>
      I have managed to create a QStandardItemModel mapper that takes a two dimensional array and creates a table model out of it. Next challange is to make it sortable.
    </p>
    <p>
      
    </p>
    <p>
      Hm, making it sortable was not really a channage.. So, the table model is quite ok now, I guess. I could now move on to implement the controls on the root project listing window. Specifically I'll need a add, change and delete project controls, that update the list and the view.
    </p>
    <p>
      
    </p>
    <p>
      After that we'll give it a bit persistence by serializing the data (via pickle).
    </p>
  </body>
</html></richcontent>
</node>
</node>
</node>
<node CREATED="1350734482080" ID="ID_1564245602" MODIFIED="1350734484929" TEXT="0.0.0"/>
<node CREATED="1350739021905" ID="ID_369826600" MODIFIED="1350739060584" TEXT="design">
<node CREATED="1350739064547" ID="ID_400227230" MODIFIED="1350913648769" TEXT="project tracking root table">
<node CREATED="1350739078642" ID="ID_269032300" MODIFIED="1350739153574" TEXT="item view model mapper"/>
<node CREATED="1350739085418" ID="ID_686260829" MODIFIED="1350739087956" TEXT="callbacks"/>
<node CREATED="1350739165112" ID="ID_1808391686" MODIFIED="1350739180551" TEXT="add / change / remove entry"/>
<node CREATED="1350739181780" ID="ID_315646437" MODIFIED="1350739184996" TEXT="sort entries"/>
<node CREATED="1350739186325" ID="ID_308712465" MODIFIED="1350739194660" TEXT="search entries"/>
<node CREATED="1350739257719" ID="ID_730909694" MODIFIED="1350739264680" TEXT="commands">
<font BOLD="true" NAME="SansSerif" SIZE="12"/>
<node CREATED="1350739266993" ID="ID_1022866824" MODIFIED="1350739278556" TEXT="test / build / deploy"/>
<node CREATED="1350739278797" ID="ID_161334498" MODIFIED="1350739294663" TEXT="git commit, pull, push"/>
<node CREATED="1350739295378" ID="ID_486630850" MODIFIED="1350739312854" TEXT="navigate directory"/>
</node>
<node CREATED="1350739199764" ID="ID_1332240827" MODIFIED="1350739211545" TEXT="details">
<font BOLD="true" NAME="SansSerif" SIZE="12"/>
<node CREATED="1350739214669" ID="ID_498107939" MODIFIED="1350739220103" TEXT="objectives">
<node CREATED="1350739337129" ID="ID_1361502312" MODIFIED="1350739339099" TEXT="primary"/>
<node CREATED="1350739339892" ID="ID_1670931225" MODIFIED="1350739341675" TEXT="secondary"/>
<node CREATED="1350739342372" ID="ID_401814301" MODIFIED="1350739344280" TEXT="tertiary"/>
</node>
<node CREATED="1350739348826" ID="ID_608813899" MODIFIED="1350739351138" TEXT="platform">
<node CREATED="1350739355932" ID="ID_148547606" MODIFIED="1350739359761" TEXT="os"/>
<node CREATED="1350739360202" ID="ID_1838284512" MODIFIED="1350739364172" TEXT="framework"/>
<node CREATED="1350739364645" ID="ID_1965348305" MODIFIED="1350739369004" TEXT="web (y/n)"/>
<node CREATED="1350739402236" ID="ID_1336411785" MODIFIED="1350739404189" TEXT="tooling">
<node CREATED="1350739408578" ID="ID_483410486" MODIFIED="1350739410244" TEXT="editor"/>
</node>
</node>
<node CREATED="1350739220424" ID="ID_1321768132" MODIFIED="1350739224084" TEXT="journal"/>
<node CREATED="1350739224542" ID="ID_1987547999" MODIFIED="1350739229087" TEXT="design">
<node CREATED="1350739329943" ID="ID_698676352" MODIFIED="1350739332363" TEXT="refactor"/>
</node>
<node CREATED="1350739229603" ID="ID_925621925" MODIFIED="1350739232360" TEXT="roadmap"/>
<node CREATED="1350739232672" ID="ID_1313911124" MODIFIED="1350739236258" TEXT="issues"/>
</node>
</node>
<node CREATED="1350739095403" FOLDED="true" ID="ID_1122947540" MODIFIED="1351003286307" TEXT="configuration">
<node CREATED="1350739115591" ID="ID_551618704" MODIFIED="1350739117255" TEXT="os"/>
<node CREATED="1350739118534" ID="ID_1309958693" MODIFIED="1350739120912" TEXT="workspace"/>
</node>
</node>
</node>
</node>
</map>
